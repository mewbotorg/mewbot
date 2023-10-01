#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Supports running the example yaml files included with mewbot, and third party plugins.

Two run configurations are supported
 - running with a specific yaml file just loads and runs the bot
 - running without a specified path will run a menu so you can choose which example you
   want to run
"""

from __future__ import annotations

from typing import Iterable

import itertools
import os
import pathlib
import sys

import mewbot.loader
from mewbot.tools.path import gather_paths, scan_paths


def gather_example_paths(*filters: str) -> Iterable[str]:
    """Locates all folders with the given names in this project's code locations."""

    # Should be the root of the repo - unless this file has been moved
    root = pathlib.Path(__file__).parent.parent.parent

    locations = itertools.chain(
        scan_paths(root, *filters, recursive=False),
        scan_paths(root / "plugins", *filters),
    )

    # Filter out the dirs which contain no yaml
    return (str(x.absolute()) for x in locations if scan_for_yaml(x))


def scan_for_yaml(target_path: str | pathlib.Path) -> bool:
    """
    Scan to see if we have a yaml file in the dir.
    """
    for _, _, files in os.walk(target_path):
        for file_name in files:
            if os.path.splitext(file_name)[1].lower() == ".yaml":
                return True
    return False


def run_example_from_argv() -> None:
    """
    Run an example directly from the argv.
    """
    if len(sys.argv) != 2:
        print("Usage", sys.argv[0], " [configuration name]")
        sys.exit(1)

    run_example_from_given_path(sys.argv[1])


def run_example_from_given_path(target_path: str) -> None:
    """
    Run an example specified off the command line.
    """

    # Extend paths so the included plugin examples can be run
    # (this is done for you in tools/examples in the top level of the repo)
    sys.path.extend(gather_paths("src"))

    with open(target_path, "r", encoding="utf-8") as config:
        bot = mewbot.loader.configure_bot("DemoBot", config)

    bot.run()


def run_examples_with_display() -> None:
    """
    Build a display for the available examples.
    """
    examples_paths = list(gather_example_paths("examples"))

    print("Welcome to mewbot! Please select an example to run.")
    yaml_map = _build_yaml_display(examples_paths)

    example_int = 0
    for _ in range(10):
        try:
            example_int = int(input("Please enter a number to run an example..."))
        except ValueError:
            print("Sorry - parse input to example no. Please try again.")
            continue

        if example_int not in yaml_map:
            print("Sorry - could not find the specific example. Please try again.")
            continue
        break

    if not example_int:
        print("No valid example provided after 10 tries.")
        sys.exit(1)

    print(f"Running {os.path.split(yaml_map[example_int])[1]}")
    run_example_from_given_path(yaml_map[example_int])


def _build_yaml_display(examples_paths: list[str]) -> dict[int, str]:
    """
    Itterate over the examples path and construct a display of all available yaml files.
    """

    yaml_map: dict[int, str] = {}
    count = 1

    for example_path in examples_paths:
        for root, _, files in os.walk(example_path):
            level = root.replace(example_path, "").count(os.sep)
            indent = "    " + " " * 4 * (level)
            print(f"{indent}{os.path.basename(root)}/")
            subindent = " " * 4 * (level + 1)

            for file_name in files:
                if os.path.splitext(file_name)[1].lower() != ".yaml":
                    continue

                yaml_map[count] = os.path.join(root, file_name)

                print(f"{count} - {subindent}{file_name}")

                count += 1

    return yaml_map


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_example_from_argv()

    elif len(sys.argv) == 1:
        run_examples_with_display()

    else:
        print("Usage: ")
        sys.exit(1)
