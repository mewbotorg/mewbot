#!/usr/bin/env python3

from __future__ import annotations

from typing import List, Generator, Set, Any, Tuple

import abc
import argparse
import dataclasses
import os
import subprocess
import sys

import pluggy  # type: ignore

PLUGIN_DEV_SPEC: Any = None
try:
    from mewbot.plugins.hook_specs import MewbotDevPluginSpec as PLUGIN_DEV_SPEC
except ModuleNotFoundError:
    # We cannot load
    PLUGIN_DEV_SPEC = None
    raise ModuleNotFoundError("We cannot import from mewbot - mewbot may not be installed")

from mewbot.plugins.hook_specs import mewbot_dev_hook_impl


@mewbot_dev_hook_impl  # type: ignore
def declare_test_locs() -> Tuple[str, ...]:
    """
    If we declare the location of this plugin's tests then they can be included in the main
    test run.
    :return:
    """
    return tuple(
        [
            os.path.split(__file__)[0],
        ]
    )


@dataclasses.dataclass
class Annotation:
    """
    Schema for a GitHub action annotation, representing an error.
    """

    level: str
    file: str
    line: int
    col: int
    title: str
    message: str

    def __str__(self) -> str:
        mess = self.message.replace("\n", "%0A")
        return (
            f"::{self.level} file={self.file},line={self.line},"
            f"col={self.col},title={self.title}::{mess}"
        )

    def __lt__(self, other: Annotation) -> bool:
        if not isinstance(other, Annotation):
            return False

        return self.file < other.file or self.file == other.file and self.line < other.line


class ToolChain(abc.ABC):
    """
    Wrapper class for running linting tools, and outputting GitHub annotations
    """

    folders: Set[str]
    is_ci: bool
    success: bool

    def __init__(self, *folders: str, in_ci: bool) -> None:
        """
        Start up this tool chain.
        :param folders:  
        :param in_ci:
        """
        self.folders = set(folders)
        self.is_ci = in_ci
        self.success = True

    def __call__(self) -> None:
        if not os.path.exists("./reports"):
            os.mkdir("./reports")

        issues = list(self.run())

        if self.is_ci:
            self.github_list(issues)

        sys.exit(not self.success or len(issues) > 0)

    @abc.abstractmethod
    def run(self) -> Generator[Annotation, None, None]:
        """Abstract function for this tool chain to run its checks"""

    def run_tool(self, name: str, *args: str) -> subprocess.CompletedProcess[bytes]:
        """Helper function to run an external binary as a check"""

        arg_list = list(args)
        arg_list.extend(self.folders)

        run_result = self._run_utility(name, arg_list)

        self.success = self.success and (run_result.returncode == 0)

        return run_result

    def _run_utility(
        self, name: str, arg_list: List[str]
    ) -> subprocess.CompletedProcess[bytes]:

        run = subprocess.run(
            arg_list,
            #stdin=subprocess.DEVNULL, capture_output=self.is_ci, check=False
        )

        if self.is_ci:
            print(f"::group::{name}")
            sys.stdout.write(run.stdout.decode("utf-8"))
            sys.stdout.write(run.stderr.decode("utf-8"))
            print("::endgroup::")

            with open(f"reports/{name}.txt", "wb") as log_file:
                log_file.write(run.stdout)
        else:
            run.stdout = b""
            run.stderr = b""

        return run

    @staticmethod
    def github_list(issues: List[Annotation]) -> None:
        """Outputs the annotations in the format for GitHub actions."""

        print("::group::Annotations")
        for issue in sorted(issues):
            print(issue)
        print("::endgroup::")

        print("Total Issues:", len(issues))


def gather_dev_paths(
    target_func: str = "declare_test_locs", pytest_windows_norm: bool = False
) -> List[str]:
    """
    Plugins can declare extra paths for the various tools.
    :param target_func: The function to execute from the hooks
                        Must return an iterable of strings
    :return:
    """
    # Cannot do much if mewbot is not installed
    if PLUGIN_DEV_SPEC is None:
        return []

    pluggy_manager = pluggy.PluginManager("mewbot_dev")
    pluggy_manager.add_hookspecs(PLUGIN_DEV_SPEC())
    pluggy_manager.load_setuptools_entrypoints("mewbotv1")

    # Load the declared src code paths
    results = getattr(pluggy_manager.hook, target_func)()  # Linter hack
    src_paths: List[str] = []
    for result_tuple in results:
        for path in result_tuple:
            if isinstance(path, str):
                src_paths.append(path)
            else:
                print(f"{path} not  a valid path")

    # When it comes to paths, pytest seems to have problems with the standard windows
    # encoding
    src_paths: List[str] = [sp.replace("\\", "/") for sp in src_paths]

    return src_paths


class TestToolchain(ToolChain):
    coverage: bool = False

    def run(self) -> Generator[Annotation, None, None]:
        args = self.build_pytest_args()

        result = self.run_tool("PyTest (Testing Framework)", *args)

        if result.returncode < 0:
            yield Annotation("error", "tools/test.py", 1, 1, "Tests Failed", "")

    def build_pytest_args(self) -> List[str]:
        """Builds out the `pytest` command

        This varies based on what output types are requested (human vs code
        readable), and whether coverage is enabled.
        Due to issues with pytest-cov handling, parallelisation is disabled
        when coverage is enabled
        https://github.com/nedbat/coveragepy/issues/1303#issuecomment-1014915146
        """

        # If additional paths are declared, we need to append them to the args

        args = [
            "pytest",
            "--new-first",  # Do uncached tests first -- likely to be more relevant.
            "--durations=0",  # Report all tests that take more than 1s to complete
            "--durations-min=1",
            "--junitxml=reports/junit.xml",
        ]

        if not self.coverage:
            args.append("--dist=load")  # Distribute between processes based on load
            args.append("--numprocesses=auto")  # Run processes equal to CPU count

            # These have to be added later - after all the rest of the args have been declared
            additional_paths = gather_dev_paths(target_func="declare_test_locs")

            args.extend(additional_paths)

            return args

        additional_cov_paths = gather_dev_paths(target_func="declare_src_locs")

        # args.append("--cov")  # Enable coverage tracking for code in the './src'
        # Need to specify coverage manually for all the relevant folder
        for target_path in additional_cov_paths:
            args.append(f"--cov={target_path}")

        args.append("--cov-report=xml:reports/coverage.xml")  # Record coverage summary in XML

        if self.is_ci:
            # Simple terminal output
            args.append("--cov-report=term")
        else:
            # Output to terminal, showing only lines which are not covered
            args.append("--cov-report=term-missing")
            # Output to html, coverage is the folder containing the output
            args.append("--cov-report=html:coverage")

        additional_test_paths = gather_dev_paths(target_func="declare_test_locs")
        args.extend(additional_test_paths)

        return args


def parse_test_options() -> argparse.Namespace:
    default = "GITHUB_ACTIONS" in os.environ

    parser = argparse.ArgumentParser(description="Run tests for mewbot")
    parser.add_argument("--ci", dest="is_ci", action="store_true", default=default)
    parser.add_argument("--cov", dest="coverage", action="store_true", default=False)

    return parser.parse_args()