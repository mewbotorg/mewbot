#!/usr/bin/env python3

import setuptools  # type: ignore

# Use the actual readme from this folder
with open("README.md", "r", encoding="utf-8") as rmf:
    long_description = rmf.read()

# Just inherit the licence from the overall project
with open("LICENSE.md", "r", encoding="utf-8") as lf:
    true_licence = lf.read()

with open("requirements.txt", "r", encoding="utf-8") as rf:
    requirements = list(x for x in rf.read().splitlines(False) if x and not x.startswith("#"))

setuptools.setup(
    name="mewbot-tests",
    version="0.0.1",
    author="Benedict Harcourt & Alex Cameron",
    install_requires="mewbot",
    author_email="mewbot@quicksilver.london",
    description="Test cases for mewbot",
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
    entry_points={"mewbotv1": ["tests = mewbot_tests"]},
    python_requires=">=3.9",  # Might be relaxed later
    py_modules=["mewbot_tests"],
)
