<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

## Install programs to prepare the working environment

The main programs used for mewbot development are
1) python
2) git
3) Some form of IDE

### 1) Install Python

If you have already done this, some of the following instructions might be different.
Uninstalling and reinstalling is probably not required, but can be a helpful debug step.

Installation media should be obtained directly from [the python downloads page][1].

#### But which version of python?

Mewbot currently targets python 3.9, 3.10 and 3.11 - as of March 2023.
We will continue to target new versions as they release.
We are currently working with python 3.9 - and these steps have been tested as working with 3.10 and 3.11

It is, often, useful to have all the versions of python which mewbot targets on your local machine.

However, you should _mostly_ use python 3.9.

The reason is that Mewbot uses several tools called linters to ensure code consistency and quality.
Linters statically analyse the code to determine if it meets certain requirements.
They should be run - and pass - before you issue a pull request to ask us to include your code in mewbot.
When such a request is issued on github, they are run automatically to check the code over.
Code which does not pass linting _cannot_ be merged.

Github runs the linters through the lowest version of python which a project targets - in this case `python3.9`.
As such, the linters will be run remotely against the code using `python3.9`.
Different versions of python have - slightly - different linting behavior.
Thus code which passes linting on `python3.9` _may_ or _may not_ pass linting by the same tool on `python3.10`.
(Is this annoying? Immensely!)

We _do not_ run linting on every version of python we target.
But we do run testing against every version of python we target.
So it's often useful to have all the versions of python we target on hand for testing purposes.
Thus, you might want to install pythons `3.9`, `3.10` and `3.11`.

#### Which linters do you use and how do I install them?

At present, these linters include
 - `black` - which ensures the code meets the python layout style guide - PEP 8 - and will reformat it to help you do this (see [here][2])
 - `mypy` - which ensure the code is fully and correctly typed - (see [here][3])
 - `flake8` - which checks for code quality and potential code smells (see [here][4])
 - `pydocstyle` - which checks the code is properly documented through doc string (see [here][5])

Don't worry about installing these - we will do that with the other python packages needed for mewbot to function.

If your code passes these linters it stands a much better chance of being correct and remaining correct into the future.
Our aim with the linters is to encourage readable, reusable, maintainable code.

#### I find the linters intimidating...

You'll get used to them surprisingly fast!
Also - while we use these linters on the main code base, we don't require that plugins use them.
So you can do many types of valuable dev work for mewbot without ever having to worrying about linters - if you don't want to.

#### Settings for python installation

During python installation
* You want to be sure the "pip" tickbox is ticked. 
      This will be used later to install the dependencies needed to run the mewbot linting scripts
* It's a bit more elegant if you select "Install for all users"
* Selecting "Add Python to environment variables" is a useful addition - but one you might want to avoid if you already have another version of python already installed. As this may cause confusion. 
      In this case you probably want to install without this ticked and use the full path to your python executable in all that follows (once you have the venv setup, this should cease to be necessary).
* The default install location is somewhat buried in the file structure. 
      I personally prefer to change it to something like "C:\Python39\" - but this is a taste thing. It shouldn't affect subsequent steps. However, it's arguably better to keep the path to the python executable short. As it cuts down on typing and potential error.

### 2) Install git

There's a number of ways to interact with git available on Windows.

There's the standard command line suite of tools - available packaged for Windows through [git-scm][6].
But there are also some very good GUIs available.
In particular the official github client for Windows - [git desktop][7].
Which does the job with no particular fuss and comes bundled with git.
It also allows you to drop into the command line if there's something particular you want to do.

HOne good reason to use git desktop over command line git is it can be slightly complex - these days - to set up git with github.
Tokens are needed for authentication and generating them is a bit of pain.

If you don't want to use git desktop, and don't want to mess around with keys for github auth, their command line tool is pretty good.

Likewise, git desktop handles all of the authentication problem for you - and you can always drop into the command line from it if there's a problem.

(For convenience, you can add `git` to your path so you can use it in any command line terminal - see the instructions [here][9]

### 3) [OPTIONAL BUT RECOMMENDED] - Install an IDE

It makes writing software a lot easier!
If you are new to software development, I heartily recommend it.

In particular, I use and like [pycharm][8] from Jetbrains.

However, it's on the expensive side and has a lot of features - resulting in a somewhat stiff learning curve.


[1]: https://www.python.org/downloads/ "Python downloads"
[2]: https://github.com/psf/black "Black main page"
[3]: https://github.com/python/mypy "mypy main page"
[4]: https://github.com/PyCQA/flake8 "flake8 main page"
[5]: http://www.pydocstyle.org/en/stable/ "pydocstyle main page"
[6]: https://git-scm.com/download/win "git-scm"
[7]: https://desktop.github.com/ "git desktop"
[8]: https://www.jetbrains.com/pycharm/ "Jetbrains Pycharm"
[9]: https://www.anujvarma.com/adding-path-variable-for-git-and-gitbash-to-work-on-windows/ "Adding git to path"
