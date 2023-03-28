#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""Development tools and helpers."""

from __future__ import annotations

import abc
import dataclasses
import os
import subprocess
import sys

from collections.abc import Iterable

from .path import gather_paths


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
        """Outputs annotations in the format used in GitHub Actions checker."""

        mess = self.message.replace("\n", "%0A")
        return (
            f"::{self.level} file={self.file},line={self.line},"
            f"col={self.col},title={self.title}::{mess}"
        )

    def __lt__(self, other: Annotation) -> bool:
        """Sorts annotations by file path and then line number."""

        if not isinstance(other, Annotation):
            return False

        return self.file < other.file or self.file == other.file and self.line < other.line


class ToolChainBaseTooling:
    """Tools which are in used in the ToolChain, but might be useful elsewhere."""

    is_ci: bool
    success: bool
    folders: set[str]

    # Stores whether each of the processes was a success or failure
    run_success: dict[str, bool]
    # Stores the raw return code of each of the processes
    run_result: dict[str, int]

    def run_tool(self, name: str, *args: str) -> subprocess.CompletedProcess[bytes]:
        """
        Helper function to run an external program as a check.

        The program will have the list of folders appended to the supplied arguments.
        If the process has a non-zero exit code, success is set to False for the chain.

        When in CI mode, this function returns the process result (including stdout and stderr),
        along with storing copies in the reports/ folder.

        :param name: The user-friendly name of the tools
        :param args: The command line to use. The first value should be the executable path.
        """

        arg_list = list(args)
        arg_list.extend(self.folders)

        run_result = self._run_utility(name, arg_list)

        self.success = run_result.returncode == 0
        self.run_success[name] = self.success
        self.run_result[name] = run_result.returncode

        return run_result

    def get_run_success(self) -> dict[str, bool]:
        """
        Provides access to the run_success object - which stores the results of the run.

        :return:
        """
        return self.run_success

    def _run_utility(
        self, name: str, arg_list: list[str]
    ) -> subprocess.CompletedProcess[bytes]:
        """
        Helper function to run an external program as a check.

        Outside of CI, the command will be given direct access to stdout/stderr and left to
        its default behaviour.

        Inside of CI, a block/group will be opened to contain the scripts output, and that
        output will be captured. Additionally, the output will be added to the reports/ folder.

        That output will also be returned to the calling code, allowing it to parse the output
        (or any generated artifacts) and emit annotations for any issues that have been found.

        :param name: The user-friendly name of the tools
        :param arg_list: The command line to use. The first value should be the executable path.
        """

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


class ToolChain(abc.ABC, ToolChainBaseTooling):
    """
    Support class for running a series of tools across the codebase.

    Each tool will be given the same set of folders, and can produce output
    to the console and/or 'annotations' indicating issues with the code.

    The behaviour of this class alters based whether it is being run in 'CI mode'.
    This mode disables all interactive and automated features of the toolchain,
    and instead outputs the state through a series of 'annotations', each one
    representing an issue the tools found.
    """

    folders: set[str]

    is_ci: bool
    # There is a scenario where a tool could fail - but not produce issues
    # This flag can be set after each tool run to EXPLICITELY fail the run if required
    fail_ci_run: bool

    # Did the most recent tool succeed?
    _success: bool

    def __init__(self, *folders: str, in_ci: bool) -> None:
        """
        Sets up a tool chain with the given settings.

        :param folders: The list of folders to run this tool against
        :param in_ci: Whether this is a run being called from a CI pipeline
        """
        self.folders = set(folders)

        self.is_ci = in_ci
        self.fail_ci_run = False

        self.success = True
        self.run_success = {}
        self.run_result = {}

    @property
    def success(self) -> bool:
        """
        Returns the success flag.
        """
        return self._success

    @success.setter
    def success(self, value: bool) -> None:
        """
        Sets the success flag.

        Also ensures the fail_ci_run flag is set True.
        This is to ensure that a ci run is failed later.
        (As success just stores the result of the last call to run_utility.
        :param value:
        :return:
        """
        self._success = value
        if value is False:
            self.fail_ci_run = True

    def execute(self) -> list[Annotation]:
        """
        Does everything in __call__ _without_ then calling sys.exit with the success code.
        """
        # Ensure the reporting location exists.
        if not os.path.exists("./reports"):
            os.mkdir("./reports")

        issues = list(self.run())

        if self.is_ci:
            self.github_list(issues)

        return issues

    def __call__(self) -> None:
        """Runs the tool chain, including exiting the script with an appropriate status code."""

        issues = self.execute()

        sys.exit(not self.success or len(issues) > 0)

    @abc.abstractmethod
    def run(self) -> Iterable[Annotation]:
        """
        Abstract function for this tool chain to run its checks.

        The function can call any number of sub-tools.
        It should set `success` to false if any tool errors or raises issues.

        When in CI mode, any issues the tool finds should be returned as Annotations.
        These will then be reported back to the CI runner.

        Outside of CI mode, the toolchain can take the action it deems most appropriate,
        including pretty messages to the user, automatically fixing, or still using annotations.
        """

    @staticmethod
    def github_list(issues: list[Annotation]) -> None:
        """
        Outputs the annotations in the format for GitHub actions.

        These are presented as group at the end of output as a work-around for
        the limit of 10 annotations per check run actually being shown on a commit or merge.
        """

        print("::group::Annotations")
        for issue in sorted(issues):
            print(issue)
        print("::endgroup::")

        print("Total Issues:", len(issues))


__all__ = ["Annotation", "ToolChain", "gather_paths"]
