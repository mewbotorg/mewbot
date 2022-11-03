from __future__ import annotations

import abc
import os

from typing import Generator, List, Set, Any

import dataclasses
import subprocess
import sys

import pluggy  # type: ignore


PLUGIN_DEV_SPEC: Any = None
try:
    from mewbot.plugins.hook_specs import MewbotDevPluginSpec as PLUGIN_DEV_SPEC
except ModuleNotFoundError:
    # We cannot load
    PLUGIN_DEV_SPEC = None


@dataclasses.dataclass
class Annotation:
    """Schema for a GitHub action annotation, representing an error"""

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
    """Wrapper class for running linting tools, and outputting GitHub annotations"""

    folders: Set[str]
    is_ci: bool
    success: bool

    def __init__(self, *folders: str, in_ci: bool) -> None:
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
            arg_list, stdin=subprocess.DEVNULL, capture_output=self.is_ci, check=False
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
