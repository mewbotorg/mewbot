#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tools for detecting paths at which source files are installed.

This file, when called directly, prints out a set of values for PYTHONPATH.
As such, it can not rely on anything that would be loaded using PYTHONPATH,
i.e. we can not use any other mewbot code from this file.
"""

from collections.abc import Iterable

import os
import pathlib


def scan_paths(
    root: pathlib.Path, *filters: str, recursive: bool = True
) -> Iterable[pathlib.Path]:
    """Scan for folders with a given name in the provided path."""

    if not recursive:
        yield from [root / name for name in filters if (root / name).exists()]
        return

    for path, children, _ in os.walk(root):
        for name in filters:
            if name in children:
                yield pathlib.Path(path) / name


def gather_paths(*filters: str) -> Iterable[str]:
    """Locates all folders with the given names in this project's code locations."""

    root = pathlib.Path(os.curdir)

    return (str(x.absolute()) for x in scan_paths(root, *filters, recursive=False))


if __name__ == "__main__":
    # When called directly, this module output the value of the PYPATH environment variable
    print(os.pathsep.join(gather_paths("src")))
