#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Supports running the example yaml files included with mewbot, and third party plugins.
"""

from __future__ import annotations

import itertools
import os
import pathlib
import sys

import mewbot.loader
from mewbot.tools.path import scan_paths, gather_paths

from collections.abc import Iterable

# Indent which will be added every level
INDENT = "  "

LEVEL_TERM_TOKEN: str = "└──"

LEVEL_CONT_TOKEN: str = "├──"

PIPE_TOKEN: str = "│"


def gather_examples_paths() -> Iterable[str]:
    """Gather all examples folders."""

    # The repo root
    root = pathlib.Path(__file__).parent.parent.parent

    example_dirs = []

    for plugin_name in os.listdir(root / "plugins"):

        example_dirs.append(scan_paths(root / "plugins" / str(plugin_name), "examples", recursive=False))

    locations = itertools.chain(
        scan_paths(root, "examples", recursive=False),
        *example_dirs
    )

    return (str(x.absolute()) for x in locations)


def _render_examples(dir_paths: list[str], accumulation: list[str], indent: str) -> None:
    """
    Render a directory - adding to the accumulation.

    :param dir_name:
    :param dirs:
    :param files:
    :return:
    """
    # Walk the entire dir - noting the files we need to render
    # This way no extraneous dirs will be rendered
    all_yaml: dict[int, pathlib.Path] = dict()

    count = 1

    accumulated_lines = []
    repo_root = pathlib.Path(__file__).parent.parent.parent

    for dir_path in dir_paths:

        dir_path = pathlib.Path(dir_path)

        assert dir_path.is_dir()

        header_added = False

        _render_dir(dir_path, accumulation=accumulated_lines, indent=indent, all_yaml=all_yaml, count=count)

    print("\n".join(accumulated_lines))


def _render_dir(target_dir: pathlib.Path, accumulation: list[str], indent: str, all_yaml: dict[int, pathlib.Path], count: int) -> None:
    """
    Render any yaml files found in a recursive dir.

    :param target_dir:
    :param accumulation:
    :param indent:
    :return:
    """
    for root, dirs, files in os.walk(target_dir):

        root_path = pathlib.Path(root)

        yaml_count = 0
        current_target_yaml = []
        for file_name in files:
            if os.path.splitext(file_name)[1].lower() == ".yaml":
                current_target_yaml.append((count, root_path / file_name))
                all_yaml[count] = root_path / file_name

                count += 1
                yaml_count += 1

        if not yaml_count:
            continue

        # Adding the header for this sub-dir
        accumulation.append(f"{LEVEL_TERM_TOKEN}{str(root)}")
        for yaml_pair in current_target_yaml:
            accumulation.append(f"{indent}{LEVEL_TERM_TOKEN} {yaml_pair[0]} {yaml_pair[1]}")

        for dir_name in dirs:
            _render_dir(target_dir= root_path / dir_name, accumulation=accumulation, indent=indent + "  ", all_yaml=all_yaml, count=count)


def build_example_maps(examples_paths: list[str]) -> tuple[list[str], dict[int, str]]:
    """
    Constructs two objects - a list of strings for output and a map between the id and example.

    :param examples_paths:
    :return example_display_list, example_keys_dict:
    """
    rendered_paths = []

    _render_examples(examples_paths, accumulation=rendered_paths, indent="")

    print("\n".join(rendered_paths))
    assert True is False, "end here"






def main() -> int:
    """
    The examples loading and running interface.

    :return:
    """
    # We're being asked to run an example directly - do that
    if len(sys.argv) == 2:
        return run_example_from_command_line()

    build_example_maps([pn for pn in gather_examples_paths()])









def run_example_from_command_line() -> int:
    """
    Run an example provided directly from the command line.

    :return:
    """

    # Extend paths so the included plugin examples can be run
    # (this is done for you in tools/examples in the top level of the repo)
    sys.path.extend(gather_paths("src"))

    with open(sys.argv[1], "r", encoding="utf-8") as config:
        bot = mewbot.loader.configure_bot("DemoBot", config)

    bot.run()

    return 0


if __name__ == "__main__":

    sys.exit(main())
