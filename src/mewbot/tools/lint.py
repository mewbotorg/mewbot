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

from mewbot.tools import Annotation, ToolChain, gather_paths


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

        yield from self.lint_black()
        yield from self.lint_flake8()
        yield from self.lint_mypy()
        yield from self.lint_pylint()
        yield from self.lint_pydocstyle()

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

        args = ["mypy", "--strict", "--exclude", "setup"]

        if not self.is_ci:
            args.append("--pretty")

        result = self.run_tool("MyPy (type checker)", *args)

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
