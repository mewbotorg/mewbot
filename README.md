<!--
SPDX-FileCopyrightText: 2021 Benedict Harcourt <ben.harcourt@harcourtprogramming.co.uk>

SPDX-License-Identifier: BSD-2-Clause
-->

# MewBot

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](CONTRIBUTORS.md)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
[![Linting](https://github.com/mewler/mewbot/actions/workflows/pylint.yml/badge.svg)](https://github.com/mewler/mewbot/actions/workflows/pylint.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=mewler_mewbot&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=mewler_mewbot)

MewBot is an automation framework intended to simplify building cross-platform
text/chat-bots.
The design is intended to be modular with configuration separated from code,
allowing users and developers to build out custom logic and behaviours with
minimal coding experience.

### Status

> :warning: This project is still in the very early stages. Some basic bots can be built
> and run, but we currently consider all parts of the framework to be unstable.

### Packages and Modules

| Package                   | Modules                             | Description                                                                                                                                |
|---------------------------|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `mewbot-core`             | `mewbot.core`                       | Base interfaces for all modules                                                                                                            |
| `mewbot-dev`              | `mewbot.component`, `mewbot.api.v1` | Development libraries + component registry system. This is the package that all 3rd party libraries should depend on for their interfaces. |
| `mewbot-runner`           | `mewbot.loader`, `mewbot.bot`       | Tools to load a bot, and run that bot.                                                                                                     |
| `mewbot-[discord/twitch]` | `mewbot.io.[discord/twitch]`        | The bindings to connect MewBot to a given service.                                                                                         |
| `mewbot-tests`            | `mewbot.tests`                      | Pytest test cases for MewBot.                                                                                                              |

![module dependency graph](./mewbot.svg)

### Development

Contributions to the project are made via GitHub pull requests, which will
enforce the code style and linting requirements of this project.

#### Setting up project for local development

The recommended way to set this project up is using python 3.9 (or higher) with
a standard `venv` setup.
The project uses a "src-dir" layout, so you will need to set up `PYTHONPATH`
with at least the `src/` directory for Python to locate the modules.
For convenience in POSIX-like systems, an importable script `./tools/path`
is provided that will return the appropriate path.

The following example will get you started in POSIX-like shells (sh, bash, zsh, etc.).

```shell
# Get the source code
git clone git@github.com:mewler/mewbot
cd mewbot

# Set up the virtual environment
python3 -m venv venv
printf '. ./tools/path\n' >>venv/bin/activate

# Activate the virtual environment
source venv/bin/activate

# Install all dependencies (including development dependencies)
pip install requirements-dev.txt

# Run a demo!
python3 -m examples examples/trivial_socket.yaml
```

#### Running the tests and linters

You can run the linters via the convenience script `./tools/lint` or with
`python -m mewbot.tools.lint`
This runs the auto-formatter `black`, two opinionated linting tools in `flake8`
and `pylint`, and the `mypy` type checker in strict mode.

You can run the test framework using the convenience script `./tools/test`
or with `python -m mewbot.tools.test`.
Locally this will default to running all tests in parallel for fast testing.
You can add the flag `--cov` to enable coverage, which will output coverage information
both to the terminal and store details of code coverage as webpages in `coverage/`.

More information on the linters and tests can be found in the
[contributor documentation](./CONTRIBUTING.md).
