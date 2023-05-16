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


# Presented as a class to make accessing some properties of the run easier.
class ReuseRun:
    """
    Represents a run of the reuse program.
    """

    paths: pathlib.Path

    def __init__(self) -> None:
        """
        Startup the reuse run.
        """
        self.paths = pathlib.Path(os.curdir)

    def get_paths(self) -> list[str]:
        """Return the targeted paths as a list of strings."""
        return [
            str(self.paths),
        ]

    def run(self) -> bool:
        """Execute reuse and return the status of the run."""
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
            str(self.paths),
        ]

        subprocess.check_call(args)
        return True


if __name__ == "__main__":
    sys.exit(0 if ReuseRun().run() else 1)
