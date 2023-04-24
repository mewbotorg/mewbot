#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""Development tools and helpers."""

from __future__ import annotations

import abc
import asyncio
import dataclasses
import os
import subprocess
import sys
from collections.abc import Iterable
from io import BytesIO

from typing import IO, BinaryIO

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

    timeout: int = 300

    def __init__(self, *folders: str, in_ci: bool) -> None:
        """
        Sets up a tool chain with the given settings.

        :param folders: The list of folders to run this tool against
        :param in_ci: Whether this is a run being called from a CI pipeline
        """
        self.folders = set(folders)
        self.is_ci = in_ci
        self.success = True

        self.loop = asyncio.get_event_loop()

    def __call__(self) -> None:
        """Runs the tool chain, including exiting the script with an appropriate status code."""
        # Windows hack to allow colour printing in the terminal
        # See https://bugs.python.org/issue30075 and our windows-dev-notes.
        if os.name == "nt":
            os.system("")

        # Ensure the reporting location exists.
        if not os.path.exists("./reports"):
            os.mkdir("./reports")

        issues = list(self.run())

        if self.is_ci:
            self.github_list(issues)

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

    def run_tool(
        self,
        name: str,
        *args: str,
        env: dict[str, str] | None = None,
        folders: set[str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        """
        Helper function to run an external program as a check.

        The program will have the list of folders appended to the supplied arguments.
        If the process has a non-zero exit code, success is set to False for the chain.

        The output of the command is made available in three different ways:
          - Output is written to reports/{tool name}.txt
          - Output and Error are returned to the caller
          - Mirror Error and Output to the terminal.

        :param name: The user-friendly name of the tools
        :param args: The command line to use. The first value should be the executable path.
        :param env: Environment variables to pass to the sub-process.
        :param folders: Override for the default set of folders for this toolchain. Use with care.
        """

        return self.loop.run_until_complete(
            self.async_run_tool(name, *args, env=env or {}, folders=folders)
        )

    async def async_run_tool(
        self, name: str, *args: str, env: dict[str, str], folders: set[str] | None = None
    ) -> subprocess.CompletedProcess[bytes]:
        """
        Helper function to run an external program as a check.

        The program will have the list of folders appended to the supplied arguments.
        If the process has a non-zero exit code, success is set to False for the chain.

        The output of the command is made available in three different ways:
          - Output is written to reports/{tool name}.txt
          - Output and Error are returned to the caller
          - Mirror Error and Output to the terminal.

        :param name: The user-friendly name of the tools
        :param args: The command line to use. The first value should be the executable path.
        :param env: Environment variables to pass to the sub-process.
        :param folders: Override for the default set of folders for this toolchain. Use with care.
        """

        arg_list = list(args)
        arg_list.extend(folders or self.folders)

        run_result = await self._run_utility(name, arg_list, env)
        assert isinstance(run_result, subprocess.CompletedProcess)

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

    async def _run_utility(
        self, name: str, arg_list: list[str], env: dict[str, str]

    ) -> subprocess.CompletedProcess[bytes]:
        """
        Helper function to run an external program as a check.

        The output of the command is made available in three different ways:
          - Output is written to reports/{tool name}.txt
          - Output and Error are returned to the caller
          - Error and Output are copied to the terminal.

        When in CI mode, we add a group header to collapse the output from each
        tool for ease of reading.

        :param name: The user-friendly name of the tools
        :param arg_list: The command line to use. The first value should be the executable path.
        :param env: Environment variables to pass to the sub-process.
        """

        # Print output header
        print(f"::group::{name}" if self.is_ci else f"\n{name}\n{'=' * len(name)}")

        env = env.copy()
        env.update(os.environ)

        process = await asyncio.create_subprocess_exec(
            *arg_list,
            stdin=subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        # MyPy validation trick -- ensure the pipes are defined (they will be).
        if not process.stdout or not process.stderr:
            raise ValueError(f"pipes for process {name} not created")

        with open(f"reports/{name}.txt", "wb") as log_file:
            # Set up the mirroring readers on the two output pipes.
            task_out = self.loop.create_task(
                read_pipe(process.stdout, sys.stdout.buffer, log_file)
            )
            task_err = self.loop.create_task(read_pipe(process.stderr, sys.stderr.buffer))

            # This is trimmed down version of subprocess.run().
            try:
                await asyncio.wait_for(process.wait(), timeout=self.timeout)
            except TimeoutError:
                process.kill()
                # run uses communicate() on windows. May be needed.
                # However, as we are running the pipes manually, it may not be.
                # Seems not to be
                await process.wait()
            # Re-raise all non-timeout exceptions.
            except:  # noqa: E722
                process.kill()
                await process.wait()
                raise
            finally:  # Ensure the other co-routines complete.
                stdout_buffer = await task_out
                stderr_buffer = await task_err

        return_code = process.returncode
        return_code = return_code if return_code is not None else 1

        run = subprocess.CompletedProcess(
            arg_list, return_code, stdout_buffer.read(), stderr_buffer.read()
        )

        if self.is_ci:
            print("::endgroup::")

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


async def read_pipe(pipe: asyncio.StreamReader, *mirrors: BinaryIO) -> IO[bytes]:
    """
    Read a pipe from a subprocess into a buffer whilst mirroring it to another pipe.
    """

    buffer = BytesIO()

    while not pipe.at_eof():
        block = await pipe.readline()
        for mirror in mirrors:
            mirror.write(block)
            mirror.flush()
        buffer.write(block)

    buffer.seek(0)
    return buffer


__all__ = ["Annotation", "ToolChain", "gather_paths"]
