#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Note - this is NOT intended to be used for local installation or as part of development.

This is intended to make this module available via pypi
It _should_ also work for local installation, but this functionality is not tested.
"""

raise NotImplementedError("Still under development.")

# from pathlib import Path
#
# import setuptools  # type: ignore
#
# # Finding the right README.md and inheriting the mewbot licence
# current_file = Path(__file__)
# root_repo_dir = current_file.parents[2]
# assert root_repo_dir.exists()
#
# with open(current_file.parent.joinpath("README.md"), "r", encoding="utf-8") as rmf:
#     long_description = rmf.read()
#
# with open(root_repo_dir.joinpath("LICENSE.md"), "r", encoding="utf-8") as lf:
#     true_licence = lf.read()
#
# with open(current_file.parent.joinpath("requirements.txt"), "r", encoding="utf-8") as rf:
#     requirements = list(x for x in rf.read().splitlines(False) if x and not x.startswith("#"))
#
#
#
# # There are a number of bits of special sauce in this call
# # - You can fill it out manually - for your project
# # - You can copy this and make the appropriate changes
# # - Or you can run "mewbot make_new_plugin" - and follow the onscreen instructions.
# #   Which should take care of most of the fiddly bits for you.
# setuptools.setup(
#     name="mewbot-discord_dice_roller",  # Note the different "-" and "_" between this
#     # and the entry_points/py_modules
#     # However, here, note it's "mewbot-" - not "mewbot_"
#     # If it's not "mewbot-" then the pattern the plugin manager uses to load plugins will fail
#     version="0.0.1",
#     author="Alex Cameron",
#     install_requires=requirements,
#     author_email="mewbot@quicksilver.london",
#     description="Example discord dice roller for mewbot",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://github.com/mewler/mewbot",
#     project_urls={
#         "Bug Tracker": "https://github.com/mewler/mewbot/issues",
#     },
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         f"License :: OSI Approved :: {true_licence}",
#         "Framework :: mewbot",
#         "Operating System :: OS Independent",
#     ],
#     package_dir={"": "src"},
#     packages=setuptools.find_packages(where="src"),
#     # see https://packaging.python.org/en/latest/specifications/entry-points/
#     # Note -
#     entry_points={"mewbot-v1": ["discord_dice_roller = mewbot_discord_dice_roller"]},
#     # Note this setup
#     # The key for the entry point should always be "mewbot"
#     # The value should be a string of the form "{prefix less name} = {py_modules name}"
#     # The "py_modules name" should match one of the py_modules declared below
#     python_requires=">=3.10",  # Might be relaxed later
#     py_modules=["mewbot_discord_dice_roller"],
# )
#
