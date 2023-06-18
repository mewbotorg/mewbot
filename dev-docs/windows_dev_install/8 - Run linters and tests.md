<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

## Test that the linters, testers e.t.c run correctly

As ever, there are several approaches to running the linters and the other utility functions.

But what do these functions do?

They all about ensuring the correctness of the code.
Bringing it into standard, useful forms and testing it to make sure it does what it claims.

There are two ways to invoke them
1) The `.sh` scripts found in the `tools` folder in the top level of the repo
2) Directly through the mewbot module

The `.sh` scripts are front ends for the python functions.
They can be run on Windows through `git bash`, but it may be easier to just invoke the functions directly through python.

### 13) Test the linters

However, before we can move onto convenience methods to more easily run the linters, we should check that they work.

#### Option 1 - Use the tools `.sh` scripts

The first way is to use the `tool.sh` scripts in the `src/tools` folder.
To do this you must

##### Acquire the capacity to run `.sh` scripts

You will now need the ability to execute `.sh` scripts.
You may already have this.
In particular, if you have installed `git` on Windows, it should come with `git-bash` (though, for reasons explained below, we will be using `git-sh`).
To check if it did, see the executable in somewhere like
```shell
C:\Program Files\Git\bin\bash.exe
```
exists.
If it does, congrats, you have bash.
If not, install it.
In either event, check the folder you found `bash.exe` in.
Also inside it should be a file called `sh.exe` - we'll be using this to run our `.sh` scripts.
(See the section "Name conflicts with `WSL`" below for why).

##### Get `sh` (and, sometimes, `bash`) on the path

This is a similar problem to getting `python` on the path.
You can either

##### Add the bash folder to the system PATH variable
This approach is probably the simplest. Use it if
* You don't already have another folder with something called `bash` on your path
* Adding the bash folder won't screw things up because of name conflicts or other reasons

1) Start the System Control Panel - search "System" and it should be the top result.
2) Select the "Advanced System Settings" submeu.
3) Click the "Environment Variables" button.
4) Under "System Variables", select "Path", then click "Edit".
5) Click New, add your python folder to the Path end of your path , and you're done
   1) (mine was "C:\Program Files\Git\bin" - but our will be where ever you've installed the executable)
   2) Thus I appended ;"C:\Program Files\Git\bin"

##### Use doskey and a pre_call.bat file to just add `sh.exe` to the path

(Instructions adapted from https://www.anujvarma.com/adding-path-variable-for-git-and-gitbash-to-work-on-windows/)

This is probably less likely to go wrong.

If you've already created this, then just append something like
```shell
doskey sh = "C:\Program Files\Git\bin\sh.exe" $*
```
(Inside the printing suppression environment, if desired, see above).

##### Name conflicts with `WSL`

Why are we using `sh.exe` not `bash.exe`?

If you have installed `WSL`, there's a problem you may be about to run into about to run into.
On systems with `WSL`, invoking `bash` causes windows to launch `WSL`.
This can be a pretty useful feature - for example, if you want to have `ubuntu` or another linux environment on your 
system to facilitate easier testing of `mewbot` on linux.
However, here, it can conflict with your ability to run `.sh` scripts.
As such, we'll be using `sh.exe` from the `Git\bin` folder, instead of `bash.sh`.
To see if this is a problem - add the `Git\bin` folder as above and type `bash` in the command prompt

If you see something like
```shell
C:\Users\[YOUR WINDOWS USERNAME]>bash
DESKTOP-C88RBET:/mnt/host/c/Users/[YOUR WSL USERNAME]#
```
Then you're getting a non-windows bash.
However, if you see something like
```shell
C:\Users\[YOUR WINDOWS USERNAME]>bash
[YOUR WINDOWS USERNAME]@DESKTOP-C88RBET MINGW64 ~
$
```
Then you're getting the "right" bash.

It's probably best to use `sh.exe` instead. 

You should get something like
```shell
C:\Users\[YOUR WINDOWS USERNAME]>sh
[YOUR WINDOWS USERNAME]@DESKTOP-C88RBET MINGW64 ~
$
```
in either case.

If not, something is wrong.
Bash is a superset of sh - so we might have to change approach in the future but, for the moment, all our `.sh` scripts work with both.

To invoke the linters using the `sh.exe` you can run something like

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>sh tools/lint
python3 could not be found
You may be on windows - trying with python not python3
NOTE - This may result in you using an unexpected version of python!
All done! ✨ 🍰 ✨
37 files left unchanged.
There are no .py[i] files in directory 'C:\mewbot_dev\mewbot\plugins\mewbot-conditions\src\mewbot_conditions.egg-info'

------------------------------------
Your code has been rated at 10.00/10

C:\mewbot_dev\mewbot\src\mewbot\tools\preflight.py:1 at module level:
        D100: Missing docstring in public module
C:\mewbot_dev\mewbot\src\mewbot\tools\reuse.py:1 at module level:
        D100: Missing docstring in public module

```

(the `pydocstyle` errors will be fixed...)

Likewise, for the testers, you might do something like

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>sh tools/test
```

Note that the path to get to the script uses  `tools/lint` _not_ `tools\lint` - we're executing in a bash-like environment and it uses linux path conventions

If you've gotten it the wrong way round, you should get an error something like this
```shell
(mewbot_venv_310) C:\mewbot_dev\mewbot>sh tools\lint
tools\lint: line 7: tools\lint/path: Not a directory
tools\lint: line 9: exec: : not found
```
).

#### Option 2 - Invoke the linters through python

As discussed previously, the `.sh` files are just wrappers for the underlying functions - which are python scripts.
As such, you can invoke them directly from the command line.

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>python -m mewbot.tools.lint
All done! ✨ 🍰 ✨
37 files left unchanged.
There are no .py[i] files in directory 'C:\mewbot_dev\mewbot\plugins\mewbot-conditions\src\mewbot_conditions.egg-info'

------------------------------------
Your code has been rated at 10.00/10

C:\mewbot_dev\mewbot\src\mewbot\tools\preflight.py:1 at module level:
        D100: Missing docstring in public module
C:\mewbot_dev\mewbot\src\mewbot\tools\reuse.py:1 at module level:
        D100: Missing docstring in public module

```

Likewise, for the testers, you might do something like

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>python -m mewbot.tools.test
```

NOTE - You _need_ to be in the root directory of your repo when you invoke the linters.
Otherwise, you might end up linting the wrong paths.

### Passing command line flags to the scripts and getting help

Each of the functions has various command line options - pass `--help` as normal with either technique to see them

e.g.

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>sh tools/test --help
python3 could not be found
You may be on windows - trying with python not python3
NOTE - This may result in you using an unexpected version of python!
usage: test.py [-h] [--ci] [--cov] [--cover [COVERING ...]] [path ...]

Run tests for mewbot

positional arguments:
  path                  Path of a file or a folder of files.

options:
  -h, --help            show this help message and exit
  --ci                  Run test in GitHub actions mode
  --cov                 Enable coverage reporting
  --cover [COVERING ...]
                        Apply coverage only to provided paths (implies --cov)
```

or

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>python -m mewbot.tools.test --help
usage: test.py [-h] [--ci] [--cov] [--cover [COVERING ...]] [path ...]

Run tests for mewbot

positional arguments:
  path                  Path of a file or a folder of files.

options:
  -h, --help            show this help message and exit
  --ci                  Run test in GitHub actions mode
  --cov                 Enable coverage reporting
  --cover [COVERING ...]
                        Apply coverage only to provided paths (implies --cov)
```

### NOTE - `black` _will_ change your files

`black` bills itself as an "opinionated" linter.
This means that it actively reformats files. 
Wit the aim of bringing them into compliance with `PEP 8`.
As such, your files _probably will_ change after `black` has been run on them.

Some IDEs, such as pycharm, will detect external file changes and update the files displayed accordingly

BEWARE - if your IDE or text editing solution DOES NOT automatically update after a file has been changed on disk.
You will need to manually reload after running `black`.

`black` is also run as part of the `lint` script. So you will also have to reload - if required - whenever you run the `lint` script.

### NOTE - `reuse` _will also_ change your files

`reuse` is responsible for ensuring that all files in the project have appropriate copyright information added to their preamble.

As such, the same warning as for `black` applies to `reuse`. 
It _will_ change you files.
Be alive to this fact.

### 14) Run the tests

Passing the `--cov` flag to the `test` script provides coverage information for the tests.

For new code, we're targeting a cover of `>80%`.

(You could also have got the same results by calling `python -m mewbot.tools.test --cov` from the command line).

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>sh tools/test --cov
================================================= test session starts =================================================
platform win32 -- Python 3.10.0, pytest-7.1.2, pluggy-1.0.0
rootdir: C:\mewbot_dev\mewbot
plugins: cov-3.0.0
collected 20 items
tests\test_core.py .......                                                                                       [ 35%]
tests\test_io_http_socket.py ..                                                                                  [ 45%]
tests\test_loader.py ...........                                                                                 [100%]
---------- coverage: platform win32, python 3.10.0-final-0 -----------
Name                                          Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------------
examples\__init__.py                              0      0      0      0   100%
examples\__main__.py                             10     10      6      0     0%   3-17
examples\discord_to_desktop_notification.py      48     48      8      0     0%   5-86
examples\trivial_discord_bot.py                  46     46      8      0     0%   5-83
examples\yaml_bot.py                             13     13      2      0     0%   3-29
src\mewbot\__init__.py                            0      0      0      0   100%
src\mewbot\api\__init__.py                        0      0      0      0   100%
src\mewbot\api\registry.py                       66     12     34      9    77%   28, 33, 44, 57, 59->52, 76, 79, 84, 89, 109-112, 118
src\mewbot\api\v1.py                            137     44     50      4    63%   38-59, 63, 68, 81, 85, 92, 95, 106, 130, 134, 142, 146, 154, 159, 167, 170-173, 177, 205, 212, 221, 226, 229-230, 233-242, 245-247
src\mewbot\bot.py                               127     85     46      0    27%   40-45, 54, 57-63, 66-72, 75-82, 102-109, 112-148, 160-169, 172-185, 188-197, 200-209
src\mewbot\config.py                             12      0      4      0   100%
src\mewbot\core.py                               87     17     24      0    83%   29, 32, 44, 47, 71, 74, 81, 84, 91, 95, 98, 101, 109, 112, 115, 118, 142
src\mewbot\data.py                               24      0      8      0   100%
src\mewbot\demo.py                               33      8      6      0    79%   11, 17, 21, 24, 27, 41, 55, 58
src\mewbot\io\__init__.py                         0      0      0      0   100%
src\mewbot\io\desktop_notification.py           114    114     36      0     0%   3-256
src\mewbot\io\discord.py                         65     65     20      0     0%   3-131
src\mewbot\io\http.py                            36     15      8      0    61%   38, 49-55, 65, 72-80, 86-91
src\mewbot\io\socket.py                          77     34     16      0    53%   50, 53-56, 59, 76-81, 89, 92-101, 106-130
src\mewbot\loader.py                             68      9     24      5    85%   30-31, 49, 56, 82-86, 118, 156
-----------------------------------------------------------------------------------------
TOTAL                                           963    520    300     18    45%
Coverage HTML written to dir .coverage_html
Required test coverage of 40.0% reached. Total coverage: 44.73%
================================================= 20 passed in 3.80s ==================================================
(mewbot_venv) C:\mewbot_dev\mewbot>
```
