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

from typing import Iterable, Optional

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
    for root, dirs, files in os.walk(target_path):
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
    examples_paths = [pn for pn in gather_example_paths("examples")]

    yaml_map: dict[int, str] = dict()
    count = 1

    print("Welcome to mewbot! Please select an example to run.")

    for example_path in examples_paths:
        for root, dirs, files in os.walk(example_path):
            level = root.replace(example_path, "").count(os.sep)
            indent = "    " + " " * 4 * (level)
            print("{}{}/".format(indent, os.path.basename(root)))
            subindent = " " * 4 * (level + 1)

            for f in files:
                if os.path.splitext(f)[1].lower() != ".yaml":
                    continue

                yaml_map[count] = os.path.join(root, f)

                print(f"{count} - {subindent}{f}")

                count += 1

    example_int = 0
    for i in range(10):
        example_int = input("Please enter a number to run an example...")

        example_int = int(example_int)

        if example_int not in yaml_map.keys():
            print("Sorry - could not find the specific example. Please try again.")
            continue
        break

    if not example_int:
        print("No valid example provided after 10 tries.")
        sys.exit(1)

    print(f"Running {os.path.split(yaml_map[example_int])[1]}")
    run_example_from_given_path(yaml_map[example_int])


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_example_from_argv()

    elif len(sys.argv) == 1:
        run_examples_with_display()

    else:
        print("Usage: ")
        sys.exit(1)
