#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Wrapper class for running linting tools.

The output of these tools will be emitted as GitHub annotations (in CI)
or default human output (otherwise).
By default, all paths declared to be part of mewbot source - either of the main
module or any installed plugins - are linted.
"""

from __future__ import annotations

from collections.abc import Iterable

import argparse
import os
import subprocess
import sys

from mewbot.tools import Annotation, ToolChain, gather_paths
from mewbot.tools.terminal import CommandDeliminator


LEVELS = frozenset({"notice", "warning", "error"})


class LintToolchain(ToolChain):
    """
    Wrapper class for running linting tools.

    The output of these tools will be emitted as GitHub annotations (in CI)
    or default human output (otherwise).
    By default, all paths declared to be part of mewbot source - either of the main
    module or any installed plugins - are linted.
    """

    def run(self) -> Iterable[Annotation]:
        """Runs the linting tools in sequence."""

        with CommandDeliminator("Starting black tool run"):
            yield from self.lint_black()
        with CommandDeliminator("Starting flake8 tool run"):
            yield from self.lint_flake8()
        with CommandDeliminator("Starting mypy tool run"):
            yield from self.lint_mypy()
        with CommandDeliminator("Starting pylint tool run"):
            yield from self.lint_pylint()
        with CommandDeliminator("Starting pydocstyle tool run"):
            yield from self.lint_pydocstyle()

        if self.is_ci and self.fail_ci_run:
            print(
                f"Some of the tools reports having silently failed!\n" f"{self.run_success}"
            )
            sys.exit(1)

    def lint_black(self) -> Iterable[Annotation]:
        """
        Run 'black', an automatic formatting tool.

        Black handles most formatting updates automatically, maintaining
        readability and code style compliance.
        """

        args = ["black"]

        if self.is_ci:
            args.extend(["--diff", "--no-color", "--quiet"])

        result = self.run_tool("Black (Formatter)", *args)

        yield from lint_black_errors(result)
        yield from lint_black_diffs(result)

    def lint_flake8(self) -> Iterable[Annotation]:
        """
        Runs 'flake8', an efficient code-style enforcer.

        flake8 is a lightweight and fast tool for finding issues relating to
        code-style, import management (both missing and unused) and a range of
        other issue.
        """

        result = self.run_tool("Flake8", "flake8")

        for line in result.stdout.decode("utf-8").split("\n"):
            if ":" not in line:
                continue

            try:
                file, line_no, col, error = line.strip().split(":", 3)
                yield Annotation("error", file, int(line_no), int(col), "", error.strip())
            except ValueError:
                pass

    def lint_mypy(self) -> Iterable[Annotation]:
        """
        Runs 'mypy', a python type analyser/linter.

        mypy enforces the requirement for type annotations, and also performs type-checking
        based on those annotations and resolvable constants.
        """

        args = ["mypy", "--strict", "--explicit-package-bases"]

        if not self.is_ci:
            args.append("--pretty")

        # MyPy does not use the stock import engine for doing its analysis,
        # so we have to give it additional hints about how the namespace package
        # structure works.
        # See https://mypy.readthedocs.io/en/stable/running_mypy.html#mapping-file-paths-to-modules
        #
        # There are two steps to this:
        #  - We set MYPYPATH equivalent to PYTHONPATH
        os.putenv("MYPYPATH", os.pathsep.join(gather_paths("src")))
        #  - We alter the folder list such that, in src-dir folders, we pass the
        #    folder of the actual pacakge (i.e. ./src/mewbot rather than ./src)
        folder_backup = self.folders
        self.folders = set(get_module_paths(*self.folders))

        # Run mypy
        result = self.run_tool("MyPy (type checker)", *args)

        # Reset the folders list.
        self.folders = folder_backup

        for line in result.stdout.decode("utf-8").split("\n"):
            if ":" not in line:
                continue

            try:
                file, line_no, level, error = line.strip().split(":", 3)
                level = level.strip()

                if level == "note":
                    level = "notice"

                level = level if level in LEVELS else "error"

                yield Annotation(level, file, int(line_no), 1, "", error.strip())
            except ValueError:
                pass

    def lint_pylint(self) -> Iterable[Annotation]:
        """
        Runs 'pylint', the canonical python linter.

        pylint performs a similar set of checks as flake8, but does so using the full
        codebase as context. As such it will also find similar blocks of code and other
        subtle issues.
        """

        result = self.run_tool("PyLint", "pylint")

        for line in result.stdout.decode("utf-8").split("\n"):
            if ":" not in line:
                continue

            try:
                file, line_no, col, error = line.strip().split(":", 3)
                yield Annotation("error", file, int(line_no), int(col), "", error)
            except ValueError:
                pass

    def lint_pydocstyle(self) -> Iterable[Annotation]:
        """
        Runs 'pydocstyle', which tests python doc blocks.

        pydocstyle checks for the existence and format of doc strings in all
        python modules, classes, and methods. These will have to be formatted
        with a single headline, arguments, return values and any extra info.
        """

        result = self.run_tool("PyDocStyle", "pydocstyle", "--match=.*\\.py$")

        lines = iter(result.stdout.decode("utf-8").split("\n"))

        for header in lines:
            if ":" not in header:
                continue

            try:
                file, line_no = header.split(" ", 1)[0].split(":")
                error = next(lines).strip()

                yield Annotation("error", file, int(line_no), 1, "", error)
            except ValueError:
                pass
            except StopIteration:
                pass


def lint_black_errors(
    result: subprocess.CompletedProcess[bytes],
) -> Iterable[Annotation]:
    """Processes 'blacks' output in to annotations."""

    errors = result.stderr.decode("utf-8").split("\n")
    for error in errors:
        error = error.strip()

        if not error:
            continue

        level, header, message, line, char, info = error.split(":", 5)
        header, _, file = header.rpartition(" ")

        level = level.strip() if level.strip() in LEVELS else "error"

        yield Annotation(level, file, int(line), int(char), message.strip(), info.strip())


def lint_black_diffs(
    result: subprocess.CompletedProcess[bytes],
) -> Iterable[Annotation]:
    """Processes 'blacks' output in to annotations."""

    file = ""
    line = 0
    buffer = ""

    for diff_line in result.stdout.decode("utf-8").split("\n"):
        if diff_line.startswith("+++ "):
            continue

        if diff_line.startswith("--- "):
            if file and buffer:
                yield Annotation("error", file, line, 1, "Black alteration", buffer)

            buffer = ""
            file, _ = diff_line[4:].split("\t")
            continue

        if diff_line.startswith("@@"):
            if file and buffer:
                yield Annotation("error", file, line, 1, "Black alteration", buffer)

            _, start, _, _ = diff_line.split(" ")
            _line, _ = start.split(",")
            line = abs(int(_line))
            buffer = ""
            continue

        buffer += diff_line + "\n"


def get_module_paths(*folders: str) -> Iterable[str]:
    """
    Covert a list of folders into modules paths.

    "src-dir" style folders will be expanded out into the paths for the
    root of each module. src-dir style roots are detected on the basis
    of being members of `sys.path`.
    """

    for path in folders:
        if path in sys.path:
            # Each folder in PYTHONPATH is considered a src-dir style collection of modules
            # We xpand these into the actual list of modules
            potential_paths = [os.path.join(path, module) for module in os.listdir(path)]
            yield from [
                module_path for module_path in potential_paths if os.path.isdir(module_path)
            ]
        else:
            # All other paths are returned unchanged
            yield path


def parse_lint_options() -> argparse.Namespace:
    """Parse command line argument for the linting tools."""

    parser = argparse.ArgumentParser(description="Run code linters for mewbot")
    parser.add_argument(
        "--ci",
        dest="is_ci",
        action="store_true",
        default="GITHUB_ACTIONS" in os.environ,
        help="Run in GitHub actions mode",
    )
    parser.add_argument(
        "--no-tests",
        dest="tests",
        action="store_false",
        default=True,
        help="Exclude tests from linting",
    )
    parser.add_argument(
        "path", nargs="*", default=[], help="Path of a file or a folder of files."
    )

    return parser.parse_args()


if __name__ == "__main__":
    options = parse_lint_options()

    paths = options.path
    if not paths:
        paths = gather_paths("src", "tests") if options.tests else gather_paths("src")

    linter = LintToolchain(*paths, in_ci=options.is_ci)
    linter()
