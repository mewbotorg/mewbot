#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Supports running the example yaml files included with mewbot, and third party plugins.
"""

from __future__ import annotations

import sys

import mewbot.loader
from mewbot.tools.path import gather_paths

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
