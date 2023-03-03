#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

from typing import Generator, List

import argparse
import os

from mewbot.tools import ToolChain, Annotation, gather_paths


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
        Due to issues with pytest-cov handling, parallelization is disabled
        when coverage is enabled
        https://github.com/nedbat/coveragepy/issues/1303#issuecomment-1014915146
        """

        # If additional paths are declared, we need to append them to the args

        args = [
            "pytest",
            "--new-first",  # Do un-cached tests first -- likely to be more relevant.
            "--durations=0",  # Report all tests that take more than 1s to complete
            "--durations-min=1",
            "--junitxml=reports/junit.xml",
        ]

        if not self.coverage:
            args.append("--dist=load")  # Distribute between processes based on load
            args.append("--numprocesses=auto")  # Run processes equal to CPU count

            # These have to be added later - after all the rest of the args have been declared
            additional_paths = gather_paths("tests")

            args.extend(additional_paths)

            return args

        additional_cov_paths = gather_paths("src")

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

        additional_test_paths = gather_paths("tests")
        args.extend(additional_test_paths)

        return args


def parse_test_options() -> argparse.Namespace:
    default = "GITHUB_ACTIONS" in os.environ

    parser = argparse.ArgumentParser(description="Run tests for mewbot")
    parser.add_argument("--ci", dest="is_ci", action="store_true", default=default)
    parser.add_argument("--cov", dest="coverage", action="store_true", default=False)

    return parser.parse_args()


if __name__ == "__main__":
    options = parse_test_options()

    testing = TestToolchain(in_ci=options.is_ci)
    testing.coverage = options.coverage
    testing()
