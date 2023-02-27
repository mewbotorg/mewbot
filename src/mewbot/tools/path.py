#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

from typing import List

import os


def gather_paths() -> List[str]:
    return ["./src", "./test"]


if __name__ == "__main__":
    print(os.pathsep.join(gather_paths()))
