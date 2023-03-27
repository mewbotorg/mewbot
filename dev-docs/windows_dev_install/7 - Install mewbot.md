<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

## Install project requirements and mewbot itself

mewbot is a composite package - it's made of several core packages and a number of additional namespace packages.
We need to install the requirements in two stages.

1) install the requirements for the core modules
2) install the requirements for the plugins

### 12) Install the project dependencies

`cd` into the dir where you cloned the mewbot repo and execute

```shell
(mewbot_venv) C:\mewbot_dev>python -m pip install -r requirements-dev.txt
```

NOTE - If you are using a `venv` Administrator privileges should not be required for this. 
They would are if you are installing the packages globally - but, because of the `venv` they are not.
One of the advantages of using a `venv` is you can change any aspect of it you like without an elevated privileges cmd window.

This will take some time.

We will return to install the plugin requirements in a moment.

### 13) Install mewbot itself

As mentioned previously there are two approaches.

#### Use .pth files to hack the venv path

You can add the repo `src` folder to a `.pth` file in the `venvs` `site-packages` folder.
See section 10 for more details.

This will allow you to import `mewbot` from python - run the tools e.t.c.
However, it does have a number of downsides.
1) It's more complex than the alternative (see below)
2) It doesn't register `mewbot` with `pip`

This means that any plugin which lists `mewbot` as a dependancy will fail to install correctly if you use it's `setup.py` file.
In fact, I would strongly recommend you _do not_ use it's setup.py file.
As this could cause `pip` to 

The advantage of this method?
It's cleaner and easier to understand.
You don't have to rely on setuptools to work correctly.
The files will be right there, and you can delete them and start again very easily.
Though it should also be fairly easy if you use the other method - see below.

(Note - if you want to work with any of the plugins in the `plugins` folder, it'd be a good idea to add this to the `.pth` file at the same time).

#### Modify the venv activation script to get mewbot on the path

This is probably the harder option, but is included for completeness.
If nothing else, it's a useful technique to know.
You can include arbitrary commands in the `venv` activation script to onfigure your working environment however you like.

In my case, the activation script could be found at

```shell
C:\mewbot_dev\mewbot_venv\Scripts\activate.bat
```

and looked like this

```shell
@echo off
rem This file is UTF-8 encoded, so we need to update the current code page while executing it
for /f "tokens=2 delims=:." %%a in ('"%SystemRoot%\System32\chcp.com"') do (
    set _OLD_CODEPAGE=%%a
)
if defined _OLD_CODEPAGE (
    "%SystemRoot%\System32\chcp.com" 65001 > nul
)
set VIRTUAL_ENV=C:\mewbot_dev\mewbot_venv
if not defined PROMPT set PROMPT=$P$G
if defined _OLD_VIRTUAL_PROMPT set PROMPT=%_OLD_VIRTUAL_PROMPT%
if defined _OLD_VIRTUAL_PYTHONHOME set PYTHONHOME=%_OLD_VIRTUAL_PYTHONHOME%
set _OLD_VIRTUAL_PROMPT=%PROMPT%
set PROMPT=(mewbot_venv) %PROMPT%
if defined PYTHONHOME set _OLD_VIRTUAL_PYTHONHOME=%PYTHONHOME%
set PYTHONHOME=
if defined _OLD_VIRTUAL_PATH set PATH=%_OLD_VIRTUAL_PATH%
if not defined _OLD_VIRTUAL_PATH set _OLD_VIRTUAL_PATH=%PATH%
set PATH=%VIRTUAL_ENV%\Scripts;%PATH%
set VIRTUAL_ENV_PROMPT=(mewbot_venv) 
:END
if defined _OLD_CODEPAGE (
    "%SystemRoot%\System32\chcp.com" %_OLD_CODEPAGE% > nul
    set _OLD_CODEPAGE=
)
```
We need to modify the `PYTHONPATH` variables as well.
Add a command such as
```shell
set PYTHONPATH=C:\mewbot_dev\mewbot;%PYTHONPATH%
```
to your `activate.bat` file - ideally somewhere between
```shell
@echo off
...
:END
```

so it won't be printed every time you activate the venv.

Save and close all open terminals.

Then open a new terminal, activate the venv, and check that `tools` can now be found by doing
```shell
(mewbot_venv) C:\Users\[YOUR WINDOWS USERNAME]>python
Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 19:00:18) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import tools
>>>
```
The primary disadvantage of this method is that it will be undone if the activation script is ever recreated.

#### RECOMMENDED APPROACH - Install mewbot in development mode

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>python setup.py develop
```

(`develop` instead of `install` means that the interpreter will use the files here instead of copying them elsewhere.
If you accidentally do `install` not `develop` ... may be best to delete the venv and start again).
If you run with `install`, you'll need to run it again every time you make changes to make sure they show up.

There are several advantages to this method

1) It's closer to production. 
        Eventually the version of `mewbot` you're hacking on will be installed using this same `setup.py` script.
2) It registers the module with `pip`.
        So it's more likely to be found by `pip` if you install another module which depends on `mewbot` in the same way.
3) It's (arguably) easier.
        You don't need to add a `.pth` file to the `venv`.

#### Conclusion

Once this is done, you are ready to enable one (or both) of the ways to run the linters and tests.

