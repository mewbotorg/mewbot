#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Supports running the example yaml files included with mewbot, and third party plugins.
"""

from __future__ import annotations

from typing import Iterable, Optional

import itertools
import os
import pathlib
import sys

import mewbot.loader


def scan_paths(
    root: pathlib.Path, *filters: str, recursive: bool = True
) -> Iterable[pathlib.Path]:
    """Scan for folders with a given name in the provided path."""

    if not recursive:
        yield from [root / name for name in filters if (root / name).exists()]
        return

    for path, children, files in os.walk(root):
        for name in filters:
            if name in children or name in files:
                yield pathlib.Path(path) / name


def gather_paths(*filters: str, search_root: Optional[str] = None) -> Iterable[str]:
    """
    Locates all folders with the given names in this project's code locations.

    :param filters: A list of dirs to search within
    :param search_root: If provided, start the search here.
                        If not, use os.curdir
    """
    if search_root is not None:
        root = pathlib.Path(search_root)
    else:
        root = pathlib.Path(os.curdir)

    locations = itertools.chain(
        scan_paths(root, *filters, recursive=False),
        scan_paths(root / "plugins", *filters),
    )

    return (str(x.absolute()) for x in locations)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage", sys.argv[0], " [configuration name]")
        sys.exit(1)

    # Extend paths so the included plugin examples can be run
    # (this is done for you in tools/examples in the top level of the repo)
    sys.path.extend(gather_paths("src"))

    with open(sys.argv[1], "r", encoding="utf-8") as config:
        bot = mewbot.loader.configure_bot("DemoBot", config)

    bot.run()
