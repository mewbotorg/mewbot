<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

## Introduction and checklist

### How to use this guide

This guide is deliberately maximalist.
It gives you a number of options for most steps.
It also shows you how to do a number of things which _might_ be useful - but are currently required for no specific step.
(They were often required in the past though - so have been included for completeness).

### What will you be able to do after following this guide?

By the end of this guide you should
1) Have a functioning `mewbot` install
2) Be able to run the `lint`, `test`, `reuse` and `preflight` scripts
3) Be able to submit code to `mewbot` with confidence it will pass the remote checks
4) Be able to run the examples
5) Be equipped with a number of tools to solve problems and set up your dev enironment the way you want it

### What does my personal setup look like?

There are a lot of options in these docs.
The choice can be somewhat overwhelming.
Here is what I do, personally, to prepare a mewbot environment for development.

This should be pretty close to what you need to do to get a working, minimally viable dev enviroment up.

This is just what I do - your setup is allowed to look very different.

1) Install all the software I need
   1) `git` - which I use mostly through `github desktop`
   2) `python` - versions `3.9`, `3.10` and `3.11`
2) Make a folder in the root of - `C:\mewbot_dev`
3) Clone the repo into it - so the files will be at `C:\mewbot_dev\mewbot`
4) Set up a command precall `.bat` file - which I use for alias'd commands and shortcuts.
        This process is intimidating, but the added utility is significant.
5) Set up a `venv` for each version of python
6) Add alias to the command precall file so I can activate each `venv` easily (e.g. the command `activate_mewbot_venv_39` will activate the `venv` for `python3.9`)
7) I will usually add other utility shortcuts to make dev easier at this time - e.g. aliasing `dir` to `ls`
8) For each `venv` I
   1) activate it
   2) cd into `C:\mewbot_dev\mewbot`
   3) Run `python -m pip install -r requirements-dev.txt` - to get the declared dev requirements
   4) Run `python setup.py develop` - to actually install mewbot
   5) Run `python -m mewbot.tools.install_deps` to install all the plugin dependencies
   6) If I want to work on plugins, I'll cd into their directory in the `plugins` folder and run `python setup.py develop` in there to install them
   7) Then I run `python -m mewbot.tools.preflight` - if this script passes, I can be reasonably confident all the linters, tests, e.t.c are running

You can find (very) detailed instructions for each of these steps in the following files.