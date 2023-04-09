<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

# Quickstart for experience developers on Windows

1) Clone the `src` somewhere sensible
2) Install the earliest version of python `mewbot` supports. The linters, tests e.t.c on the remote host run on the earliest version of python supported by mewbot - at present `3.9`. So we suggest using this for dev.
3) As ever, we recommend using a `venv`, but it's up to you. If you do, activate it now.
4) `cd` into the cloned `mewbot` repo
5) Install requirements for the main program with `pip install -r requirements-dev.txt` (or `python -m pip install -r requirements-dev.txt` if you don't have `pip` on the path)
6) Install requirements for the plugins with `python -m mewbot.tools.install_deps`
7) Run `python setup.py develop`
8) If you can run `sh` scripts easily, you can run the `sh` scripts in `tools` (`lint`, `test`, `reuse` e.t.c)
9) If you can't, you can run them through `python -m mewbot.tools.lint` e.t.c (the `sh` scripts are just wrappers around these functions)
10) Before you commit, please run the `preflight` tool. Which duplicates the checks that would be run remotely anyway. This checks that
    1) The linters pass
    2) The tests pass
    3) `reuse` has been run
11) Enjoy development!