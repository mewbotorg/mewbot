#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

import setuptools  # type: ignore

with open("README.md", "r", encoding="utf-8") as rmf:
    long_description = rmf.read()

with open("LICENSE.md", "r", encoding="utf-8") as lf:
    true_licence = lf.read()

setuptools.setup(
    name="mewbot",
    version="0.0.1",
    author="Benedict Harcourt & Alex Cameron",
    author_email="mewbot@tea-cats.co.uk & mewbot@quicksilver.london",
    description="Lightweight, YAML-driven, text based, generic irc Bot framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mewler/mewbot",
    project_urls={
        "Bug Tracker": "https://github.com/mewler/mewbot/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        f"License :: OSI Approved :: {true_licence}",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src", exclude=('mewbot.tools', 'examples')),
    python_requires=">=3.9",  # Might be relaxed later
)
