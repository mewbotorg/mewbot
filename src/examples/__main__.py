#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

# There are two ways this can be run
# - if you pass the path of a mewbot yaml configuration to this script it will be run
# - if you pass no paths in, you get an interactive view from which you can select what to be run
# - - this allows you to run examples which are declared by mewbot plugins installed on the system
# - - these will be included as virtual folders in the examples dir

from __future__ import annotations

from typing import Iterable, Sequence, Tuple

import pathlib
import os
import sys

import mewbot.api.registry
import mewbot.loader
import mewbot.tools


# Any yaml file names which should not be offered as options to the user
YAML_FILTER_LIST: Tuple[str] = ("examples_to_filter_go_here.yaml",)


def main() -> None:
    """
    If no arguments are passed to the function, assumes that we want the listing view of all
    available examples.
    Including ones from installed plugins.
    :return:
    """
    examples = list(locate_examples())

    # Display the available paths and also assign the paths to numbers
    list_examples(examples)
    # Ask the user for the bot they want to run
    index = select_example(examples)
    # Run the bot
    load_and_run_bot(str(examples[index]))


def locate_examples() -> Iterable[pathlib.Path]:
    """Load modules from setuptools that declare a `mewbotv1` entrypoint.

    :return: the loaded objects.
    """

    for root in mewbot.tools.gather_paths("examples"):
        for path, _, files in os.walk(root):
            for file in [
                f for f in files if f.endswith(".yaml") and f not in YAML_FILTER_LIST
            ]:
                yield pathlib.Path(os.path.join(path, file))


def list_examples(paths: Sequence[pathlib.Path]) -> None:
    """
    List out the examples that are available to run.
    :param paths: List of valid example files
    """
    print("Available Examples")

    for path in paths:
        print(f" {path}")


def select_example(paths: Sequence[pathlib.Path]) -> int:
    """
    Ask the user for a valid path number.
    :return:
    """
    rtn_val: str = input("Please enter the number of the bot to run...\n")

    while True:
        try:
            selected = int(rtn_val)
        except ValueError:
            rtn_val = input("Not a valid bot number. Please enter again...\n")
            continue

        if not 0 < selected < len(paths):
            rtn_val = input("Number did not correspond to a bot - please try again\n")
            continue

        return selected


def load_and_run_bot(yaml_path: str) -> None:
    """
    Load and run a bot from a given path.
    :param yaml_path:
    :return:
    """
    assert os.path.isfile(
        yaml_path
    ), f"Error - cannot run bot at {yaml_path} - yaml file does not exist"

    with open(yaml_path, "r", encoding="utf-8") as config:
        bot = mewbot.loader.configure_bot("DemoBot", config)

    bot.run()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage", sys.argv[0], " [configuration name]")
        sys.exit(1)

    if len(sys.argv) == 2:
        load_and_run_bot(sys.argv[1])
    else:
        main()
