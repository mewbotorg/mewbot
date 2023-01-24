#!/usr/bin/env python3

import setuptools  # type: ignore

with open("README.md", "r", encoding="utf-8") as rmf:
    long_description = rmf.read()

with open("LICENSE.md", "r", encoding="utf-8") as lf:
    true_licence = lf.read()

with open("requirements.txt", "r", encoding="utf-8") as rf:
    requirements = list(x for x in rf.read().splitlines(False) if x and not x.startswith("#"))

setuptools.setup(
    name="mewbot",
    version="0.0.1",
    author="Benedict Harcourt & Alex Cameron",
    author_email="mewbot@tea-cats.co.uk & mewbot@quicksilver.london",
    description="Lightweight, YAML-driven, text based, generic irc Bot framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=true_licence,
    url="https://github.com/mewler/mewbot",
    project_urls={
        "Bug Tracker": "https://github.com/mewler/mewbot/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        f"License :: OSI Approved :: {true_licence}",
        "Framework :: Mewbot",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    entry_points={"mewbotv1": ["main = mewbot"]},
    python_requires=">=3.9",  # Might be relaxed later
    install_requires=requirements
)
