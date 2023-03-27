# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Uses the reuse tool to ensure copyright info is present in all files.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

COPYRIGHT: str = "Mewbot Developers <mewbot@quicksilver.london>"
LICENSE: str = "BSD-2-Clause"


def main() -> bool:
    """Automatically install all plugins into the current working tree."""

    dot = pathlib.Path(os.curdir)

    args: list[str] = [
        "reuse",
        "annotate",
        "--merge-copyrights",
        "--copyright",
        COPYRIGHT,
        "--license",
        LICENSE,
        "--skip-unrecognised",
        "--skip-existing",
        "--recursive",
        str(dot),
    ]

    subprocess.check_call(args)
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
