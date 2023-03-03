# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

from typing import List

import os
import pathlib
import subprocess
import sys


def main() -> bool:
    dot = pathlib.Path()
    targets: List[str] = []

    if not (dot / "setup.py").exists():
        print("Unable to find setup.py in current folder")
        print("This script expects to be run from the root of the mewbot repo")
        return False

    targets.append(str(dot))

    for path, _, files in os.walk(dot / "plugins"):
        if "setup.py" in files:
            targets.append(path)

    subprocess.check_call([sys.executable, "-m", "pip", "install", *targets])
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
