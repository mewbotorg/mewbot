#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tools for detecting paths at which source files are installed.

This file, when called directly, prints out a set of values for PYTHONPATH.
As such, it can not rely on anything that would be loaded using PYTHONPATH,
i.e. we can not all any other mewbot code from this file.
"""

from typing import Iterable

import itertools
import os
import pathlib


def scan_paths(
    root: pathlib.Path, *filters: str, recursive: bool = True
) -> Iterable[pathlib.Path]:
    if not recursive:
        yield from [root / name for name in filters if (root / name).exists()]
        return

    for path, children, _ in os.walk(root):
        for name in filters:
            if name in children:
                yield pathlib.Path(path) / name


def gather_paths(*filters: str) -> Iterable[str]:
    root = pathlib.Path(os.curdir)

    return [
        str(x.absolute())
        for x in itertools.chain(
            scan_paths(root, *filters, recursive=False),
            scan_paths(root / "plugins", *filters),
        )
    ]


if __name__ == "__main__":
    print(os.pathsep.join(gather_paths("src")))
