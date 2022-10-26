#!/usr/bin/env python3

from __future__ import annotations

from typing import Generator, Set, List, Any

import os
import subprocess

import pluggy  # type: ignore

from tools.common import Annotation, ToolChain

PLUGIN_DEV_SPEC: Any = None
try:
    from mewbot.plugins.hook_specs import MewbotDevPluginSpec as PLUGIN_DEV_SPEC
except ModuleNotFoundError:
    # We cannot load
    PLUGIN_DEV_SPEC = None

LEVELS: Set[str] = {"notice", "warning", "error"}


class LintToolchain(ToolChain):
    """Wrapper class for running linting tools, and outputting GitHub annotations"""

    def run(self) -> Generator[Annotation, None, None]:
        yield from self.lint_black()
        yield from self.lint_flake8()
        yield from self.lint_mypy()
        yield from self.lint_pylint()

    def lint_black(self) -> Generator[Annotation, None, None]:
        args = ["black"]

        if self.is_ci:
            args.extend(["--diff", "--no-color", "--quiet"])

        result = self.run_tool("Black (Formatter)", *args)

        yield from lint_black_errors(result)
        yield from lint_black_diffs(result)

    def lint_flake8(self) -> Generator[Annotation, None, None]:
        result = self.run_tool("Flake8", "flake8")

        for line in result.stdout.decode("utf-8").split("\n"):
            if ":" not in line:
                continue

            try:
                file, line_no, col, error = line.strip().split(":", 3)
                yield Annotation("error", file, int(line_no), int(col), "", error.strip())
            except ValueError:
                pass

    def lint_mypy(self) -> Generator[Annotation, None, None]:
        args = ["mypy", "--strict"]

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

    def lint_pylint(self) -> Generator[Annotation, None, None]:
        result = self.run_tool("PyLint", "pylint")

        for line in result.stdout.decode("utf-8").split("\n"):
            if ":" not in line:
                continue

            try:
                file, line_no, col, error = line.strip().split(":", 3)
                yield Annotation("error", file, int(line_no), int(col), "", error)
            except ValueError:
                pass


def lint_black_errors(
    result: subprocess.CompletedProcess[bytes],
) -> Generator[Annotation, None, None]:
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
) -> Generator[Annotation, None, None]:
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


def gather_extra_linting_paths() -> List[str]:
    """
    Gather the paths which the plugins have declared should be added to linting.
    :return:
    """
    pluggy_manager = pluggy.PluginManager("mewbot_dev")

    # This is the bit which might be a problem - if mewbot itself is not installed
    if PLUGIN_DEV_SPEC is None:
        return []

    pluggy_manager.add_hookspecs(PLUGIN_DEV_SPEC())
    pluggy_manager.load_setuptools_entrypoints("mewbotv1")

    # Losd the declared src code paths
    results = getattr(pluggy_manager.hook, "declare_src_locs")()  # Linter hack
    src_paths: List[str] = []
    for result_tuple in results:
        for path in result_tuple:
            if isinstance(path, str):
                src_paths.append(path)
            else:
                print(f"{path} not  a valid path")

    return src_paths


if __name__ == "__main__":
    is_ci = "GITHUB_ACTIONS" in os.environ

    base_paths = ["src", "examples", "tests", "tools"]
    extra_paths = gather_extra_linting_paths()
    base_paths.extend(extra_paths)

    linter = LintToolchain(*base_paths, in_ci=is_ci)
    linter()
