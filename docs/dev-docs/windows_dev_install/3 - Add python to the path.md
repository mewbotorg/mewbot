<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

## Add python to the path - optional but recommended

This allows you to more easily invoke python for testing purposes.
It's also quite a handy utility program to be called on as needed.

### 4) OPTIONAL - Modify the path to include python

NOTE - You can safely skip this step if you intend to use a `venv`.
Which is highly recommended for software development.

### Should you do this?

The aim of this step is to allow you to invoke `python` from the command line - typing something like

```shell
Microsoft Windows [Version 10.0.19045.2728]
(c) Microsoft Corporation. All rights reserved.
C:\Users\[YOUR WINDOWS USERNAME]>python
Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 19:00:18) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```
(my default python is `3.10` - yours could be `3.11` or otherwise).

You could work directly with the full path to the python executable in subsequent steps, but this might be a little verbose.

If you're using a `venv`, once you activate it, the version of python associated with that `venv` will be on the path anyway as `python`.
It's more useful to do this if you might be using python for other things - and it's just a bit faster all round.

#### Check to see if you have to do this at all

To check if python is on the path open a command prompt - by typing "cmd" in the search or otherwise (this prompt need not be in administrator mode - in fact, this should never be needed with this instructions) and type "python".
Or the path to your python executable.

This should yield something like

```shell
Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 19:00:18) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

Which should match the version of python you installed above.

If this did not work, you can add python to the path manually (optionally under a different name).

There are many approaches to adding something to the path - which to use depends on your individual needs.

#### Approach 1 - Adding the python root folder to system path

This approach is probably the simplest. Use it if
* You don't already have another python on your path
* Adding the python folder won't screw things up because of name conflicts or other reasons

1) Start the System Control Panel - search "System" and it should be the top result.
2) Select the "Advanced System Settings" submeu.
3) Click the "Environment Variables" button.
4) Under "System Variables", select "Path", then click "Edit".
5) Click New, add your python folder to the Path, and you're done (mine was "C:\Python310\" - but our will be where ever you've installed the executable)

(adapted from the instructions found [here][1])

#### Approach 2 - Don't modify the path at all and use doskey

doskey allows you to alias functions on Windows.

Usually the alias' do not persist between sessions, but you can create what's referred to as a "command precall" file which will be executed every time a terminal is opened in windows.
This has considerable advantages - alias' for common functions can speed up and greatly simplify your workflow.

Starting by creating a list of alias you want to be run everytime the terminal starts up.
For the moment, this should just be something like

```shell
DOSKEY python = C:\\Python310\\python.exe $*
```

One advantage of this is it allows for multiple versions of python to - somewhat - elegantly co-exist. You could have, for example

```shell
DOSKEY python310 = C:\\Python310\\python.exe $*
```

which is handy if you want to test mewbot against multiple different versions of python.

It is a bit more work, but does allow some greatly increased flexibility in your development environmnt.

(NOTE - the `$*` at the end of the line - this will pass through any command line arguments to the interpreter.
If you do not include this, then you will not be able to execute any commands which involve command line arguments.)

(NOTE - `doskey` can be lower or upper case - as with most commands to the Windows shell - it's equivalent).

To create a set of `doskey` shortcuts

1) Define a list of the alis or other commands that you want to run every time the terminal starts.
2) Then create a .bat file containing those commands.
3) Mine just contained, for the moment
       `python = C:\\Python310\\python.exe $*`
4) Open regedit and navigate to "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Command Processor"
5) Create a new, string variable. Call it "AutoRun" - note the capitalisation - and value it with the absolute path to the .bat file you previously created.
        (I put mine inside my python folder for convenience. But you could put yours anywhere really).
6) Close all open terminals.
7) Test function by opening a new cmd prompt and typing "python" - check you're getting the right python with
       `import sys` then `print(sys.executable)`
8) Add new commands to the .bat file freely.


(adapted from [here][2])


By default, the commands in this file will be printed to the terminal every time it's opened.
You could do something like this

```shell
@echo off
DOSKEY python = C:\\Python310\\python.exe $*
:END
```

which will suppress printing.

(Note - if something like
```shell
python -m pip
```
does not work - which involves passing command line arguments to the python interpreter - you might have forgotten the `$*` on the end of the line.
This character allows passing through all command line arguments to the underlying, aliased command
).

For more `doskey` options, see

https://stackoverflow.com/questions/20530996/aliases-in-windows-command-prompt

#### Further options

You can add arbitrary code to this file - which will be executed every time a terminal is open.

The `.bat` is referred to as a command precall file.

[1]: https://www.itprotoday.com/windows-server/how-can-i-add-new-folder-my-system-path "Changing Windows Path"
[2]: https://stackoverflow.com/questions/20530996/aliases-in-windows-command-prompt "Running commands every time the cmd prompt is opened"