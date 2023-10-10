#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Custom setup.py to install some, or all, mewbot pckages.

A hacked up setup.py which will install all of `src` as one package locally,
but is used to build multiple packages for publishing.

This script works only in certain edge cases, namely when setuptools is using
the package name as the temporary directories (otherwise, multiple invocations
will cause cross-talk with modules being included in packages they should not
be in).

You can install the entire codebase using normal methods such as
  ./setup.py install

Or you can install one specific sub package (e.g. mewbot-io) with
  ./setup.py io install

However, doing so may cause weird dependency issues if a copy of mewbot-core
with the same version is not installed.
"""

import os.path
import sys

from typing import Dict, List, Set, Union

import setuptools

PACKAGES: Set[str] = {"", "io", "core", "api", "test"}


def load_requirements(requirements: List[str], file: str) -> None:
    """
    Parse a requirements.txt into file into a set of dependencies.

    Note that this function does not follow `-r` or process and other flags.
    """

    if not os.path.exists(file):
        return

    with open(file, "r", encoding="utf-8") as rf:
        requirements.extend(
            x for x in rf.read().splitlines(False) if x and not x.startswith("#")
        )


def main() -> None:
    """
    Wrap setuptools with dynamically generated packages and information.
    """

    version = "0.0.2"
    config: Dict[str, Union[str, List[str]]] = {
        "version": version,
        "author": "Mewbot Developers (https://github.com/mewbotorg)",
        "author_email": "mewbot@quicksilver.london",
        "description": "Lightweight, YAML-driven, text based, generic irc Bot framework",
        "license_files": ["LICENSE.md"],
        "url": "https://github.com/mewler/mewbot",
        "python_requires": ">=3.10",
        "classifiers": [
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            "License :: OSI Approved :: BSD License",
        ],
        "package_data": {"": ["py.typed"]},
        "project_urls": {
            "Bug Tracker": "https://github.com/mewler/mewbot/issues",
        },
    }

    with open("README.md", "r", encoding="utf-8") as rmf:
        config["long_description"] = rmf.read()
        config["long_description_content_type"] = "text/markdown"

    if sys.argv[1] in PACKAGES:
        package = sys.argv.pop(1)

        name = f"mewbot-{package}" if package else "mewbot"
        packages = [f"mewbot.{package}"] if package else ["mewbot"]

        # All sub-packages depend on mewbot-core except mewbot-core itself.
        requirements = [f"mewbot-core=={version}"] if package != "core" else []

        load_requirements(requirements, f"requirements-{package}.txt")
    else:
        name = "mewbot"
        packages = setuptools.find_packages("src")
        requirements = []
        load_requirements(requirements, "requirements.txt")
        for package in PACKAGES:
            load_requirements(requirements, f"requirements-{package}.txt")

    setuptools.setup(
        name=name,
        package_dir={"": "src"},
        packages=packages,
        install_requires=requirements,
        **config,
    )


if __name__ == "__main__":
    main()
