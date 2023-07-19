#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

import os
from pathlib import Path

import setuptools  # type: ignore

# Finding the right README.md and inheriting the mewbot licence
current_file = Path(__file__)
root_repo_dir = current_file.parents[2]
assert root_repo_dir.exists()

with open(current_file.parent.joinpath("README.md"), "r", encoding="utf-8") as rmf:
    long_description = rmf.read()

with open(current_file.parent.joinpath("requirements.txt"), "r", encoding="utf-8") as rf:
    requirements = list(x for x in rf.read().splitlines(False) if x and not x.startswith("#"))

# Reading the LICENSE file and parsing the results
# LICENSE file should contain a symlink to the licence in the LICENSES folder
# Held in the root of the repo

with Path("LICENSE.md").open("r", encoding="utf-8") as license_file:
    license_text = license_file.read()

cand_full_license_path = Path(license_text.strip())

# We have a symlink to the license - read it
if cand_full_license_path.exists():
    true_license_ident = os.path.splitext(license_text.split(r"/")[-1])[0]

    with cand_full_license_path.open("r", encoding="utf-8") as true_license_file:
        true_license_text = true_license_file.read()

else:
    raise NotImplementedError(
        f"Cannot programmatically determine license_ident from license. "
        f"Link '{license_text}' may be invalid. "
        "If you have added your own license in the LICENSE.md file, please move it to the "
        "LICENSES folder in the root of the repo and replace the LICENSE.md file wih a symlink "
        "to that resource."
    )

# There are a number of bits of special sauce in this call
# - You can fill it out manually - for your project
# - You can copy this and make the appropriate changes
# - Or you can run "mewbot make_namespace_plugin" - and follow the onscreen instructions.
#   Which should take care of most of the fiddly bits for you.
setuptools.setup(
    name="mewbot-io-file-system-input",
    version="0.0.1",
    author="Alex Cameron",
    install_requires=requirements,
    author_email="mewbot@quicksilver.london",
    description="Mewbot Developers (https://github.com/mewbotorg)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mewler/mewbot",
    project_urls={
        "Bug Tracker": "https://github.com/mewler/mewbot/issues",
    },
    license=true_license_text,
    classifiers=[
        "Programming Language :: Python :: 3",
        f"License :: OSI Approved :: {true_license_ident}",
        "Framework :: mewbot",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src", include=["mewbot.*"]),
    # see https://packaging.python.org/en/latest/specifications/entry-points/
    # Note -
    entry_points={"mewbot_v1": ["file_system_monitor_io = mewbot.io.file_system_monitor"]},
    # Note this setup
    # The key for the entry point should always be "mewbot"
    # The value should be a string of the form "{prefix less name} = {py_modules name}"
    # The "py_modules name" should match one of the py_modules declared below
    python_requires=">=3.10",  # Might be relaxed later
)
