#!/usr/bin/env python3

import setuptools  # type: ignore

# Use the actual readme from this folder
with open("README.md", "r", encoding="utf-8") as rmf:
    long_description = rmf.read()

# Just inherit the licence from the overall project
with open("LICENSE.md", "r", encoding="utf-8") as lf:
    true_licence = lf.read()

# There are a number of bits of special sauce in this call
# - You can fill it out manually - for your project
# - You can copy this and make the appropriate changes
# - Or you can run "mewbot make_new_plugin" - and follow the onscreen instructions.
#   Which should take care of most of the fiddly bits for you.
setuptools.setup(
    name="mewbot-conditions",  # Note the different "-" and "_" between this
    # and the entry_points/py_modules
    # However, here, note it's "mewbot-" - not "mewbot_"
    # If it's not "mewbot-" then the pattern the plugin manager uses to load plugins will fail
    version="0.0.1",
    author="Alex Cameron",
    install_requires="mewbot",
    author_email="mewbot@quicksilver.london",
    description="Example discord dice roller for mewbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mewler/mewbot",
    project_urls={
        "Bug Tracker": "https://github.com/mewler/mewbot/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        f"License :: OSI Approved :: {true_licence}",
        "Framework :: mewbot",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    # see https://packaging.python.org/en/latest/specifications/entry-points/
    # Note -
    entry_points={"mewbotv1": ["conditions = mewbot_conditions"]},
    # Note this setup
    # The key for the entry point should always be "mewbot"
    # The value should be a string of the form "{prefix less name} = {py_modules name}"
    # The "py_modules name" should match one of the py_modules declared below
    python_requires=">=3.9",  # Might be relaxed later
    py_modules=["mewbot_conditions"],
)
