<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

[//]: # (mewbot_docs_do_not_include)

# Attempt 1 - Naive and unlikely to work

python -m venv C:\mewbot_dev\mewbot_install_test
C:\mewbot_dev\mewbot_install_test\Scripts\activate
python
pip list
python -m pip install --upgrade pip
cd C:\mewbot_dev\mewbot
python setup.py api develop
pip list
python setup.py core develop
pip list
python setup.py develop
pip list
python setup.py io develop
pip list
python setup.py test develop
cd plugins\mewbot-io-discord
python setup.py develop
pip list
python setup.py core develop
cd ..
cd .
cd ..
python setup.py core develop
pip list
doskey/history


(mewbot_install_test) C:\mewbot_dev\mewbot>pip list
Package            Version Editable project location
------------------ ------- --------------------------------------------------
colorama           0.4.6
coverage           7.2.5
exceptiongroup     1.1.1
execnet            1.9.0
feedparser         6.0.10
importlib-metadata 6.6.0
iniconfig          2.0.0
mewbot             0.0.1   c:\mewbot_dev\mewbot\src
mewbot-api         0.0.1   c:\mewbot_dev\mewbot\src
mewbot-core        0.0.1   c:\mewbot_dev\mewbot\src
mewbot-io          0.0.1   c:\mewbot_dev\mewbot\src
mewbot-io-discord  0.0.1   c:\mewbot_dev\mewbot\plugins\mewbot-io-discord\src
mewbot-test        0.0.1   c:\mewbot_dev\mewbot\src
packaging          23.1
pip                23.1.2
pluggy             1.0.0
py-cord            2.4.1
pytest             7.3.1
pytest-asyncio     0.21.0
pytest-cov         4.0.0
pytest-xdist       3.3.0
setuptools         57.4.0
tomli              2.0.1
win10toast         0.9
zipp               3.15.0



## Notes

To my considerable surprise worked, and seemed to be importing from the right places.
Ish.
mypy is not happy.
Complaining about duplicate files being found in the search path.

# Attempt 2 - I don't think we need mewbot itself if we have all the parts of it

cd C:\mewbot_dev\working_dir
python -m venv C:\mewbot_dev\mewbot_install_test
C:\mewbot_dev\mewbot_install_test\Scripts\activate

python  # Checking we have the right interpreter
pip list

python -m pip install --upgrade pip
cd C:\mewbot_dev\mewbot

python setup.py core develop
pip list

python setup.py api develop
pip list

python setup.py develop
pip list
python setup.py io develop
pip list
python setup.py test develop
cd plugins\mewbot-io-discord
python setup.py develop
pip list
python setup.py core develop
cd ..
cd .
cd ..
python setup.py core develop
pip list
doskey/history

## Notes

mypy is still broken.
Action: Need to check if mypy actually works if we install from pypi
Result: Yes, it very much does. The problem is the methodology here, not mypy.

# Attempt 3 - just install the base module

Will need to deal with how to install functionally from pip later.

cd C:\mewbot_dev\working_dir
mypy
python -m venv C:\mewbot_dev\mewbot_install_test
C:\mewbot_dev\mewbot_install_test\Scripts\activate
python
pip list
python -m pip install --upgrade pip
cd C:\mewbot_dev\mewbot
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip list
python setup.py core develop
doskey/history

Got some deprecated warnings.
Think it might be best to work directly through pip locally.


### Note - check if mypy runs before you start anything.

If it does, and you don't install it in your venv, you may get misleading results.

In fact, in general, it's a good idea to check the state of the pip before running anything.

# Attempt 4 - using just pip

cd C:\mewbot_dev\working_dir
python -m venv C:\mewbot_dev\mewbot_install_test
C:\mewbot_dev\mewbot_install_test\Scripts\activate
python -m pip install --upgrade pip
pip install -e C:\mewbot_dev\mewbot
pip list
pip install -e C:\mewbot_dev\mewbot core
mypy src
cd C:\mewbot_dev\mewbot
mypy src
python -m mypy src
pip install mypy
python -m mypy src
doskey/history

mypy is seeing the same file in two different places - again - which makes it unhappy.

Using pip may be a dead end - pip seems to do some kind of path manipulation under the hood which is producing unhelpful results.

# Attempt 5 - boosted just using pip

cd C:\mewbot_dev\working_dir
python -m venv C:\mewbot_dev\mewbot_install_test
C:\mewbot_dev\mewbot_install_test\Scripts\activate
python -m pip install --upgrade pip
cd C:\mewbot_dev\mewbot
pip install -r requirements-dev.txt
pip install -e C:\mewbot_dev\mewbot
mypy src

(mewbot_install_test) C:\mewbot_dev\mewbot>mypy src
src\mewbot\tools\path.py: error: Source file found twice under different module names: "tools.path" and "mewbot.tools.path"
Found 1 error in 1 file (errors prevented further checking)

doskay/history
doskey/history

mypy - Needs to grow up and learn to deal with multiple paths to the same file.
python doesn't care - why should it's type linting subsystem?

# Attempt 6 - I just want a working installation at this point

cd C:\mewbot_dev\working_dir
python -m venv C:\mewbot_dev\mewbot_install_test
C:\mewbot_dev\mewbot_install_test\Scripts\activate
python -m pip install --upgrade pip
cd C:\mewbot_dev\mewbot
pip install -r requirements-dev.txt
python setup.py develop
mypy src

Success: no issues found in 22 source files

doskey/history

## That worked

Okay. Fairish indications that using pip to install causes the problem.
Why?
Pip may be adding the path and then running setup.py.
Some of the notes in setuptools talks about how using pip installable may be causing problems - such as undesired files getting in there.

https://setuptools.pypa.io/en/latest/userguide/development_mode.html

From the notes there

```
“Strict” editable installs
When thinking about editable installations, users might have the following expectations:

It should allow developers to add new files (or split/rename existing ones) and have them automatically exposed.

It should behave as close as possible to a regular installation and help users to detect problems (e.g. new files not being included in the distribution).

Unfortunately these expectations are in conflict with each other. To solve this problem setuptools allows developers to choose a more “strict” mode for the editable installation. This can be done by passing a special configuration setting via pip, as indicated below:

pip install -e . --config-settings editable_mode=strict

In this mode, new files won’t be exposed and the editable installs will try to mimic as much as possible the behavior of a regular install. Under the hood, setuptools will create a tree of file links in an auxiliary directory ($your_project_dir/build) and add it to PYTHONPATH via a .pth file. (Please be careful to not delete this repository by mistake otherwise your files may stop being accessible).

```


```
Legacy Behavior
If your project is not compatible with the new “editable installs” or you wish to replicate the legacy behavior, for the time being you can also perform the installation in the compat mode:

pip install -e . --config-settings editable_mode=compat
This installation mode will try to emulate how python setup.py develop works (still within the context of PEP 660).

Warning

The compat mode is transitional and will be removed in future versions of setuptools, it exists only to help during the migration period. Also note that support for this mode is limited: it is safe to assume that the compat mode is offered “as is”, and improvements are unlikely to be implemented. Users are encouraged to try out the new editable installation techniques and make the necessary adaptations.

Note

Newer versions of pip no longer run the fallback command python setup.py develop when the pyproject.toml file is present. This means that setting the environment variable SETUPTOOLS_ENABLE_FEATURES="legacy-editable" will have no effect when installing a package with pip.
```

This seems to be a bad solution.

So trying not to use pip entirely.

## Running with the current version for the moment

```shell
Package                                 Version   Editable project location
--------------------------------------- --------- -------------------------
aiohttp                                 3.8.4
aiosignal                               1.3.1
astroid                                 2.15.5
async-timeout                           4.0.2
attrs                                   23.1.0
binaryornot                             0.4.4
black                                   23.3.0
boolean.py                              4.0
chardet                                 5.1.0
charset-normalizer                      3.1.0
click                                   8.1.3
colorama                                0.4.6
coverage                                7.2.5
dill                                    0.3.6
exceptiongroup                          1.1.1
execnet                                 1.9.0
feedparser                              6.0.10
flake8                                  6.0.0
frozenlist                              1.3.3
idna                                    3.4
importlib-metadata                      6.6.0
iniconfig                               2.0.0
isort                                   5.12.0
Jinja2                                  3.1.2
lazy-object-proxy                       1.9.0
license-expression                      30.1.0
MarkupSafe                              2.1.2
mccabe                                  0.7.0
mewbot                                  0.0.1     c:\mewbot_dev\mewbot\src
mewbot-core                             0.0.1
multidict                               6.0.4
mypy                                    1.3.0
mypy-extensions                         1.0.0
packaging                               23.1
pathspec                                0.11.1
pip                                     23.1.2
platformdirs                            3.5.1
pluggy                                  1.0.0
py-cord                                 2.4.1
pycodestyle                             2.10.0
pydeps                                  1.12.7
pydocstyle                              6.3.0
pyflakes                                3.0.1
pylint                                  2.17.4
pypiwin32                               223
pytest                                  7.3.1
pytest-asyncio                          0.21.0
pytest-cov                              4.0.0
pytest-github-actions-annotate-failures 0.2.0
pytest-xdist                            3.3.1
python-debian                           0.1.49
pywin32                                 306
PyYAML                                  6.0
reuse                                   1.1.2
setuptools                              67.8.0
sgmllib3k                               1.0.0
snowballstemmer                         2.2.0
stdlib-list                             0.8.0
tomli                                   2.0.1
tomlkit                                 0.11.8
types-PyYAML                            6.0.12.10
typing_extensions                       4.5.0
win10toast                              0.9
wrapt                                   1.15.0
yarl                                    1.9.2
zipp                                    3.15.0
```

We have mewbot and mewbot core appearing in the list twice

```shell
Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 19:00:18) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import mewbot.core as test_core
>>> test_core.__file__
'c:\\mewbot_dev\\mewbot\\src\\mewbot\\core\\__init__.py'
>>> import mewbot
>>> mewbot.core
<module 'mewbot.core' from 'c:\\mewbot_dev\\mewbot\\src\\mewbot\\core\\__init__.py'>
>>>
```

We _probably_ don't have a problem.

Going to try just installing the other mewbot modules

## SAVE POINT

No, I can't be arsed to dupe the venv.
Good idea tho.
But I want to test it all the way through.

cd C:\mewbot_dev\working_dir
python -m venv C:\mewbot_dev\mewbot_install_test
C:\mewbot_dev\mewbot_install_test\Scripts\activate
python -m pip install --upgrade pip
cd C:\mewbot_dev\mewbot
pip install -r requirements-dev.txt
python setup.py develop
mypy src
doskey/history
pip list
python
mypy src
doskey/history

## Installing mewbot-api - via pip

pip install mewbot-api

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>pip list
Package                                 Version   Editable project location
--------------------------------------- --------- -------------------------
aiohttp                                 3.8.4
aiosignal                               1.3.1
astroid                                 2.15.5
async-timeout                           4.0.2
attrs                                   23.1.0
binaryornot                             0.4.4
black                                   23.3.0
boolean.py                              4.0
chardet                                 5.1.0
charset-normalizer                      3.1.0
click                                   8.1.3
colorama                                0.4.6
coverage                                7.2.5
dill                                    0.3.6
exceptiongroup                          1.1.1
execnet                                 1.9.0
feedparser                              6.0.10
flake8                                  6.0.0
frozenlist                              1.3.3
idna                                    3.4
importlib-metadata                      6.6.0
iniconfig                               2.0.0
isort                                   5.12.0
Jinja2                                  3.1.2
lazy-object-proxy                       1.9.0
license-expression                      30.1.0
MarkupSafe                              2.1.2
mccabe                                  0.7.0
mewbot                                  0.0.1     c:\mewbot_dev\mewbot\src
mewbot-api                              0.0.1
mewbot-core                             0.0.1
multidict                               6.0.4
mypy                                    1.3.0
mypy-extensions                         1.0.0
packaging                               23.1
pathspec                                0.11.1
pip                                     23.1.2
platformdirs                            3.5.1
pluggy                                  1.0.0
py-cord                                 2.4.1
pycodestyle                             2.10.0
pydeps                                  1.12.7
pydocstyle                              6.3.0
pyflakes                                3.0.1
pylint                                  2.17.4
pypiwin32                               223
pytest                                  7.3.1
pytest-asyncio                          0.21.0
pytest-cov                              4.0.0
pytest-github-actions-annotate-failures 0.2.0
pytest-xdist                            3.3.1
python-debian                           0.1.49
pywin32                                 306
PyYAML                                  6.0
reuse                                   1.1.2
setuptools                              67.8.0
sgmllib3k                               1.0.0
snowballstemmer                         2.2.0
stdlib-list                             0.8.0
tomli                                   2.0.1
tomlkit                                 0.11.8
types-PyYAML                            6.0.12.10
typing_extensions                       4.5.0
win10toast                              0.9
wrapt                                   1.15.0
yarl                                    1.9.2
zipp                                    3.15.0
```

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>python
Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 19:00:18) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import mewbot.api as api_test
>>> api_test.__file__
'C:\\mewbot_dev\\mewbot_install_test\\lib\\site-packages\\mewbot\\api\\__init__.py'
>>>
```

...sod.

Okay. It worked for mewbot-core, but not mewbot-api. Why?

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>pip install d20
Collecting d20
  Using cached d20-1.1.2-py3-none-any.whl (20 kB)
Collecting cachetools>=3.1.0 (from d20)
  Using cached cachetools-5.3.0-py3-none-any.whl (9.3 kB)
Collecting lark-parser~=0.9.0 (from d20)
  Using cached lark_parser-0.9.0-py2.py3-none-any.whl
Installing collected packages: lark-parser, cachetools, d20
Successfully installed cachetools-5.3.0 d20-1.1.2 lark-parser-0.9.0

(mewbot_install_test) C:\mewbot_dev\mewbot>mypy src
src\mewbot\io\common.py:54: error: Return type "AsyncIterable[None]" of "act" incompatible with return type "Coroutine[Any, Any, None]" in supertype "Action"  [override]
src\mewbot\io\common.py:211: error: Return type "AsyncIterable[OutputEvent]" of "act" incompatible with return type "Coroutine[Any, Any, None]" in supertype "Action"  [override]
src\examples\rss_input.py:44: error: Return type "AsyncIterable[None]" of "act" incompatible with return type "Coroutine[Any, Any, None]" in supertype "Action"  [override]
Found 3 errors in 2 files (checked 22 source files)

(mewbot_install_test) C:\mewbot_dev\mewbot>
```

pip _may_ not be broken.
mypy is not happy

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>pip uninstall mewbot-api
Found existing installation: mewbot-api 0.0.1
Uninstalling mewbot-api-0.0.1:
  Would remove:
    c:\mewbot_dev\mewbot_install_test\lib\site-packages\mewbot\api\*
    c:\mewbot_dev\mewbot_install_test\lib\site-packages\mewbot_api-0.0.1.dist-info\*
Proceed (Y/n)? y
  Successfully uninstalled mewbot-api-0.0.1

(mewbot_install_test) C:\mewbot_dev\mewbot>mypy src
Success: no issues found in 22 source files

(mewbot_install_test) C:\mewbot_dev\mewbot>
```

fixes the problem.

## Install mewbot-api - via setup.py

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>python setup.py api develop
running develop
C:\mewbot_dev\mewbot_install_test\lib\site-packages\setuptools\command\develop.py:40: EasyInstallDeprecationWarning: easy_install command is deprecated.
!!

        ********************************************************************************
        Please avoid running ``setup.py`` and ``easy_install``.
        Instead, use pypa/build, pypa/installer, pypa/build or
        other standards-based tools.

        See https://github.com/pypa/setuptools/issues/917 for details.
        ********************************************************************************

!!
  easy_install.initialize_options(self)
C:\mewbot_dev\mewbot_install_test\lib\site-packages\setuptools\_distutils\cmd.py:66: SetuptoolsDeprecationWarning: setup.py install is deprecated.
!!

        ********************************************************************************
        Please avoid running ``setup.py`` directly.
        Instead, use pypa/build, pypa/installer, pypa/build or
        other standards-based tools.

        See https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html for details.
        ********************************************************************************

!!
  self.initialize_options()
running egg_info
creating src\mewbot_api.egg-info
writing src\mewbot_api.egg-info\PKG-INFO
writing dependency_links to src\mewbot_api.egg-info\dependency_links.txt
writing requirements to src\mewbot_api.egg-info\requires.txt
writing top-level names to src\mewbot_api.egg-info\top_level.txt
writing manifest file 'src\mewbot_api.egg-info\SOURCES.txt'
reading manifest file 'src\mewbot_api.egg-info\SOURCES.txt'
adding license file 'LICENSE.md'
writing manifest file 'src\mewbot_api.egg-info\SOURCES.txt'
running build_ext
Creating c:\mewbot_dev\mewbot_install_test\lib\site-packages\mewbot-api.egg-link (link to src)
mewbot-api 0.0.1 is already the active version in easy-install.pth

Installed c:\mewbot_dev\mewbot\src
Processing dependencies for mewbot-api==0.0.1
Searching for importlib-metadata==6.6.0
Best match: importlib-metadata 6.6.0
Adding importlib-metadata 6.6.0 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for mewbot-core==0.0.1
Best match: mewbot-core 0.0.1
mewbot-core 0.0.1 is already the active version in easy-install.pth

Using c:\mewbot_dev\mewbot\src
Searching for zipp==3.15.0
Best match: zipp 3.15.0
Adding zipp 3.15.0 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Finished processing dependencies for mewbot-api==0.0.1

(mewbot_install_test) C:\mewbot_dev\mewbot>
```

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>pip list
Package                                 Version   Editable project location
--------------------------------------- --------- -------------------------
aiohttp                                 3.8.4
aiosignal                               1.3.1
astroid                                 2.15.5
async-timeout                           4.0.2
attrs                                   23.1.0
binaryornot                             0.4.4
black                                   23.3.0
boolean.py                              4.0
cachetools                              5.3.0
chardet                                 5.1.0
charset-normalizer                      3.1.0
click                                   8.1.3
colorama                                0.4.6
coverage                                7.2.5
d20                                     1.1.2
dill                                    0.3.6
exceptiongroup                          1.1.1
execnet                                 1.9.0
feedparser                              6.0.10
flake8                                  6.0.0
frozenlist                              1.3.3
idna                                    3.4
importlib-metadata                      6.6.0
iniconfig                               2.0.0
isort                                   5.12.0
Jinja2                                  3.1.2
lark-parser                             0.9.0
lazy-object-proxy                       1.9.0
license-expression                      30.1.0
MarkupSafe                              2.1.2
mccabe                                  0.7.0
mewbot                                  0.0.1     c:\mewbot_dev\mewbot\src
mewbot-api                              0.0.1     c:\mewbot_dev\mewbot\src
mewbot-core                             0.0.1
multidict                               6.0.4
mypy                                    1.3.0
mypy-extensions                         1.0.0
packaging                               23.1
pathspec                                0.11.1
pip                                     23.1.2
platformdirs                            3.5.1
pluggy                                  1.0.0
py-cord                                 2.4.1
pycodestyle                             2.10.0
pydeps                                  1.12.7
pydocstyle                              6.3.0
pyflakes                                3.0.1
pylint                                  2.17.4
pypiwin32                               223
pytest                                  7.3.1
pytest-asyncio                          0.21.0
pytest-cov                              4.0.0
pytest-github-actions-annotate-failures 0.2.0
pytest-xdist                            3.3.1
python-debian                           0.1.49
pywin32                                 306
PyYAML                                  6.0
reuse                                   1.1.2
setuptools                              67.8.0
sgmllib3k                               1.0.0
snowballstemmer                         2.2.0
stdlib-list                             0.8.0
tomli                                   2.0.1
tomlkit                                 0.11.8
types-PyYAML                            6.0.12.10
typing_extensions                       4.5.0
win10toast                              0.9
wrapt                                   1.15.0
yarl                                    1.9.2
zipp                                    3.15.0
```

mypy seems happy.
That seemed to be pointing to the right files.

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>python
Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 19:00:18) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import mewbot.core as test_core
>>> test_core.__file__
'c:\\mewbot_dev\\mewbot\\src\\mewbot\\core\\__init__.py'
>>>
```

mewbot.core is not _reporting_ an editable path.
But does, indeed, appear to be editable.

## Now trying to install discord

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>pip install -r plugins\mewbot-io-discord\requirements.txt
Requirement already satisfied: py-cord~=2.4.0 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from -r plugins\mewbot-io-discord\requirements.txt (line 3)) (2.4.1)
Requirement already satisfied: mewbot.api==0.0.1 in c:\mewbot_dev\mewbot\src (from -r plugins\mewbot-io-discord\requirements.txt (line 6)) (0.0.1)
Requirement already satisfied: mewbot-core==0.0.1 in c:\mewbot_dev\mewbot\src (from mewbot.api==0.0.1->-r plugins\mewbot-io-discord\requirements.txt (line 6)) (0.0.1)
Requirement already satisfied: importlib-metadata~=6.6.0 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from mewbot.api==0.0.1->-r plugins\mewbot-io-discord\requirements.txt (line 6)) (6.6.0)
Requirement already satisfied: aiohttp<3.9.0,>=3.6.0 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from py-cord~=2.4.0->-r plugins\mewbot-io-discord\requirements.txt (line 3)) (3.8.4)
Requirement already satisfied: typing-extensions<5,>=4 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from py-cord~=2.4.0->-r plugins\mewbot-io-discord\requirements.txt (line 3)) (4.5.0)
Requirement already satisfied: attrs>=17.3.0 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from aiohttp<3.9.0,>=3.6.0->py-cord~=2.4.0->-r plugins\mewbot-io-discord\requirements.txt (line 3)) (23.1.0)
Requirement already satisfied: charset-normalizer<4.0,>=2.0 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from aiohttp<3.9.0,>=3.6.0->py-cord~=2.4.0->-r plugins\mewbot-io-discord\requirements.txt (line 3)) (3.1.0)
Requirement already satisfied: multidict<7.0,>=4.5 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from aiohttp<3.9.0,>=3.6.0->py-cord~=2.4.0->-r plugins\mewbot-io-discord\requirements.txt (line 3)) (6.0.4)
Requirement already satisfied: async-timeout<5.0,>=4.0.0a3 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from aiohttp<3.9.0,>=3.6.0->py-cord~=2.4.0->-r plugins\mewbot-io-discord\requirements.txt (line 3)) (4.0.2)
Requirement already satisfied: yarl<2.0,>=1.0 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from aiohttp<3.9.0,>=3.6.0->py-cord~=2.4.0->-r plugins\mewbot-io-discord\requirements.txt (line 3)) (1.9.2)
Requirement already satisfied: frozenlist>=1.1.1 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from aiohttp<3.9.0,>=3.6.0->py-cord~=2.4.0->-r plugins\mewbot-io-discord\requirements.txt (line 3)) (1.3.3)
Requirement already satisfied: aiosignal>=1.1.2 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from aiohttp<3.9.0,>=3.6.0->py-cord~=2.4.0->-r plugins\mewbot-io-discord\requirements.txt (line 3)) (1.3.1)
Requirement already satisfied: zipp>=0.5 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from importlib-metadata~=6.6.0->mewbot.api==0.0.1->-r plugins\mewbot-io-discord\requirements.txt (line 6)) (3.15.0)
Requirement already satisfied: idna>=2.0 in c:\mewbot_dev\mewbot_install_test\lib\site-packages (from yarl<2.0,>=1.0->aiohttp<3.9.0,>=3.6.0->py-cord~=2.4.0->-r plugins\mewbot-io-discord\requirements.txt (line 3)) (3.4)
```

After correcting a typo in to requirements.txt

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>python plugins\mewbot-io-discord\setup.py develop
running develop
C:\mewbot_dev\mewbot_install_test\lib\site-packages\setuptools\command\develop.py:40: EasyInstallDeprecationWarning: easy_install command is deprecated.
!!

        ********************************************************************************
        Please avoid running ``setup.py`` and ``easy_install``.
        Instead, use pypa/build, pypa/installer, pypa/build or
        other standards-based tools.

        See https://github.com/pypa/setuptools/issues/917 for details.
        ********************************************************************************

!!
  easy_install.initialize_options(self)
C:\mewbot_dev\mewbot_install_test\lib\site-packages\setuptools\_distutils\cmd.py:66: SetuptoolsDeprecationWarning: setup.py install is deprecated.
!!

        ********************************************************************************
        Please avoid running ``setup.py`` directly.
        Instead, use pypa/build, pypa/installer, pypa/build or
        other standards-based tools.

        See https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html for details.
        ********************************************************************************

!!
  self.initialize_options()
running egg_info
writing src\mewbot_io_discord.egg-info\PKG-INFO
writing dependency_links to src\mewbot_io_discord.egg-info\dependency_links.txt
writing entry points to src\mewbot_io_discord.egg-info\entry_points.txt
writing requirements to src\mewbot_io_discord.egg-info\requires.txt
writing top-level names to src\mewbot_io_discord.egg-info\top_level.txt
reading manifest file 'src\mewbot_io_discord.egg-info\SOURCES.txt'
adding license file 'LICENSE.md'
writing manifest file 'src\mewbot_io_discord.egg-info\SOURCES.txt'
running build_ext
Creating c:\mewbot_dev\mewbot_install_test\lib\site-packages\mewbot-io-discord.egg-link (link to src)
mewbot-io-discord 0.0.1 is already the active version in easy-install.pth

Installed c:\mewbot_dev\mewbot\src
Processing dependencies for mewbot-io-discord==0.0.1
Searching for mewbot-api==0.0.1
Best match: mewbot-api 0.0.1
mewbot-api 0.0.1 is already the active version in easy-install.pth

Using c:\mewbot_dev\mewbot\src
Searching for py-cord==2.4.1
Best match: py-cord 2.4.1
Adding py-cord 2.4.1 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for importlib-metadata==6.6.0
Best match: importlib-metadata 6.6.0
Adding importlib-metadata 6.6.0 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for mewbot-core==0.0.1
Best match: mewbot-core 0.0.1
mewbot-core 0.0.1 is already the active version in easy-install.pth

Using c:\mewbot_dev\mewbot\src
Searching for typing-extensions==4.5.0
Best match: typing-extensions 4.5.0
Adding typing-extensions 4.5.0 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for aiohttp==3.8.4
Best match: aiohttp 3.8.4
Adding aiohttp 3.8.4 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for zipp==3.15.0
Best match: zipp 3.15.0
Adding zipp 3.15.0 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for aiosignal==1.3.1
Best match: aiosignal 1.3.1
Adding aiosignal 1.3.1 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for frozenlist==1.3.3
Best match: frozenlist 1.3.3
Adding frozenlist 1.3.3 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for yarl==1.9.2
Best match: yarl 1.9.2
Adding yarl 1.9.2 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for async-timeout==4.0.2
Best match: async-timeout 4.0.2
Adding async-timeout 4.0.2 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for multidict==6.0.4
Best match: multidict 6.0.4
Adding multidict 6.0.4 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for charset-normalizer==3.1.0
Best match: charset-normalizer 3.1.0
Adding charset-normalizer 3.1.0 to easy-install.pth file
Installing normalizer-script.py script to C:\mewbot_dev\mewbot_install_test\Scripts
Installing normalizer.exe script to C:\mewbot_dev\mewbot_install_test\Scripts

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for attrs==23.1.0
Best match: attrs 23.1.0
Adding attrs 23.1.0 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for idna==3.4
Best match: idna 3.4
Adding idna 3.4 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Finished processing dependencies for mewbot-io-discord==0.0.1
```

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>pip list
Package                                 Version   Editable project location
--------------------------------------- --------- -------------------------
aiohttp                                 3.8.4
aiosignal                               1.3.1
astroid                                 2.15.5
async-timeout                           4.0.2
attrs                                   23.1.0
binaryornot                             0.4.4
black                                   23.3.0
boolean.py                              4.0
cachetools                              5.3.0
chardet                                 5.1.0
charset-normalizer                      3.1.0
click                                   8.1.3
colorama                                0.4.6
coverage                                7.2.5
d20                                     1.1.2
dill                                    0.3.6
exceptiongroup                          1.1.1
execnet                                 1.9.0
feedparser                              6.0.10
flake8                                  6.0.0
frozenlist                              1.3.3
idna                                    3.4
importlib-metadata                      6.6.0
iniconfig                               2.0.0
isort                                   5.12.0
Jinja2                                  3.1.2
lark-parser                             0.9.0
lazy-object-proxy                       1.9.0
license-expression                      30.1.0
MarkupSafe                              2.1.2
mccabe                                  0.7.0
mewbot                                  0.0.1     c:\mewbot_dev\mewbot\src
mewbot-api                              0.0.1     c:\mewbot_dev\mewbot\src
mewbot-core                             0.0.1
mewbot-io-discord                       0.0.1     c:\mewbot_dev\mewbot\src
multidict                               6.0.4
mypy                                    1.3.0
mypy-extensions                         1.0.0
packaging                               23.1
pathspec                                0.11.1
pip                                     23.1.2
platformdirs                            3.5.1
pluggy                                  1.0.0
py-cord                                 2.4.1
pycodestyle                             2.10.0
pydeps                                  1.12.7
pydocstyle                              6.3.0
pyflakes                                3.0.1
pylint                                  2.17.4
pypiwin32                               223
pytest                                  7.3.1
pytest-asyncio                          0.21.0
pytest-cov                              4.0.0
pytest-github-actions-annotate-failures 0.2.0
pytest-xdist                            3.3.1
python-debian                           0.1.49
pywin32                                 306
PyYAML                                  6.0
reuse                                   1.1.2
setuptools                              67.8.0
sgmllib3k                               1.0.0
snowballstemmer                         2.2.0
stdlib-list                             0.8.0
tomli                                   2.0.1
tomlkit                                 0.11.8
types-PyYAML                            6.0.12.10
typing_extensions                       4.5.0
win10toast                              0.9
wrapt                                   1.15.0
yarl                                    1.9.2
zipp                                    3.15.0
```

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>python
Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 19:00:18) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import mewbot.io.discord as test_module
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ModuleNotFoundError: No module named 'mewbot.io.discord'
>>>
```

... not. Great.

Turned out to be the installation methodology...

```shell
(mewbot_install_test) C:\mewbot_dev\mewbot>cd plugins\mewbot-io-discord

(mewbot_install_test) C:\mewbot_dev\mewbot\plugins\mewbot-io-discord>python setup.py develop
running develop
C:\mewbot_dev\mewbot_install_test\lib\site-packages\setuptools\command\develop.py:40: EasyInstallDeprecationWarning: easy_install command is deprecated.
!!

        ********************************************************************************
        Please avoid running ``setup.py`` and ``easy_install``.
        Instead, use pypa/build, pypa/installer, pypa/build or
        other standards-based tools.

        See https://github.com/pypa/setuptools/issues/917 for details.
        ********************************************************************************

!!
  easy_install.initialize_options(self)
C:\mewbot_dev\mewbot_install_test\lib\site-packages\setuptools\_distutils\cmd.py:66: SetuptoolsDeprecationWarning: setup.py install is deprecated.
!!

        ********************************************************************************
        Please avoid running ``setup.py`` directly.
        Instead, use pypa/build, pypa/installer, pypa/build or
        other standards-based tools.

        See https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html for details.
        ********************************************************************************

!!
  self.initialize_options()
running egg_info
writing src\mewbot_io_discord.egg-info\PKG-INFO
writing dependency_links to src\mewbot_io_discord.egg-info\dependency_links.txt
writing entry points to src\mewbot_io_discord.egg-info\entry_points.txt
writing requirements to src\mewbot_io_discord.egg-info\requires.txt
writing top-level names to src\mewbot_io_discord.egg-info\top_level.txt
reading manifest file 'src\mewbot_io_discord.egg-info\SOURCES.txt'
writing manifest file 'src\mewbot_io_discord.egg-info\SOURCES.txt'
running build_ext
Creating c:\mewbot_dev\mewbot_install_test\lib\site-packages\mewbot-io-discord.egg-link (link to src)
Removing mewbot-io-discord 0.0.1 from easy-install.pth file
Adding mewbot-io-discord 0.0.1 to easy-install.pth file
detected new path 'c:\\mewbot_dev\\mewbot\\src'

Installed c:\mewbot_dev\mewbot\plugins\mewbot-io-discord\src
Processing dependencies for mewbot-io-discord==0.0.1
Searching for mewbot-api==0.0.1
Best match: mewbot-api 0.0.1
mewbot-api 0.0.1 is already the active version in easy-install.pth

Using c:\mewbot_dev\mewbot\src
Searching for py-cord==2.4.1
Best match: py-cord 2.4.1
Adding py-cord 2.4.1 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for importlib-metadata==6.6.0
Best match: importlib-metadata 6.6.0
Adding importlib-metadata 6.6.0 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for mewbot-core==0.0.1
Best match: mewbot-core 0.0.1
mewbot-core 0.0.1 is already the active version in easy-install.pth

Using c:\mewbot_dev\mewbot\src
Searching for typing-extensions==4.5.0
Best match: typing-extensions 4.5.0
Adding typing-extensions 4.5.0 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for aiohttp==3.8.4
Best match: aiohttp 3.8.4
Adding aiohttp 3.8.4 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for zipp==3.15.0
Best match: zipp 3.15.0
Adding zipp 3.15.0 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for aiosignal==1.3.1
Best match: aiosignal 1.3.1
Adding aiosignal 1.3.1 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for frozenlist==1.3.3
Best match: frozenlist 1.3.3
Adding frozenlist 1.3.3 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for yarl==1.9.2
Best match: yarl 1.9.2
Adding yarl 1.9.2 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for async-timeout==4.0.2
Best match: async-timeout 4.0.2
Adding async-timeout 4.0.2 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for multidict==6.0.4
Best match: multidict 6.0.4
Adding multidict 6.0.4 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for charset-normalizer==3.1.0
Best match: charset-normalizer 3.1.0
Adding charset-normalizer 3.1.0 to easy-install.pth file
Installing normalizer-script.py script to C:\mewbot_dev\mewbot_install_test\Scripts
Installing normalizer.exe script to C:\mewbot_dev\mewbot_install_test\Scripts

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for attrs==23.1.0
Best match: attrs 23.1.0
Adding attrs 23.1.0 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Searching for idna==3.4
Best match: idna 3.4
Adding idna 3.4 to easy-install.pth file

Using c:\mewbot_dev\mewbot_install_test\lib\site-packages
Finished processing dependencies for mewbot-io-discord==0.0.1

(mewbot_install_test) C:\mewbot_dev\mewbot\plugins\mewbot-io-discord>python
Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 19:00:18) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import mewbot.io.discord as test
>>> exit()
```

Trying the same for the dice roller _seemed_ to work

# Current candidate commands

python -m venv C:\mewbot_dev\mewbot_install_test
C:\mewbot_dev\mewbot_install_test\Scripts\activate
python -m pip install --upgrade pip
cd C:\mewbot_dev\mewbot
pip install -r requirements-dev.txt
python setup.py develop
mypy src
doskey/history
pip list
python
mypy src
doskey/history
pip install mewbot-api
pip list
python
pip install d20
mypy src
pip uninstall mewbot-api
mypy src
python setup.py api develop
pip list
mypy src
python
pip install -r plugins\mewbot-discord_dice_roller\requirements.txt
pip install -r plugins\mewbot-io-discord\requirements.txt
python
python plugins\mewbot-io-discord\setup.py develop
mypy src
pip list
sh tools/tests
sh tools/test
pip list
python
cd plugins\mewbot-io-discord
python setup.py develop
python
cd../
cd ../
mypy src
sh tools/lint
mypy src
sh tools/lint
python
python examples plugins\mewbot-discord_dice_roller\examples\direct_import_dice_roller_bot.yaml
python src\examples plugins\mewbot-discord_dice_roller\examples\direct_import_dice_roller_bot.yaml
cd plugins\mewbot-discord_dice_roller
python setup.py develop
pip list
python
doskey/history

# Attempt 7 - Streamlining

Now trying to get the commands down to as few as possible and still working.

cd C:\mewbot_dev\
mkdir C:\mewbot_dev\mewbot_working_dir
cd C:\mewbot_dev\mewbot_working_dir
python -m venv C:\mewbot_dev\mewbot_install_test_2
C:\mewbot_dev\mewbot_install_test_2\Scripts\activate
python -m pip install --upgrade pip

cd C:\mewbot_dev\mewbot
sh tools/install-deps

cd C:\mewbot_dev\mewbot\plugins\mewbot-io-discord
python setup.py develop

cd ..\mewbot-discord_dice_roller
python setup.py develop

pip uninstall mewbot-api
pip uninstall mewbot-core
cd C:\mewbot_dev\mewbot
python setup.py api develop
pip uninstall mewbot-core
python setup.py core develop
python setup.py api develop
pip uninstall mewbot-api
python setup.py api develop

### Got us to where we needed to be. Now trying.

mkdir C:\mewbot_dev\mewbot_working_dir
cd C:\mewbot_dev\mewbot_working_dir
python -m venv C:\mewbot_dev\mewbot_install_test_2
C:\mewbot_dev\mewbot_install_test_2\Scripts\activate
python -m pip install --upgrade pip

cd C:\mewbot_dev\mewbot
sh tools/install-deps

cd C:\mewbot_dev\mewbot\plugins\mewbot-io-discord
python setup.py develop

cd ..\mewbot-discord_dice_roller
python setup.py develop

pip uninstall -y mewbot-api
pip uninstall -y mewbot-core
pip uninstall -y mewbot-io
pip uninstall -y mewbot-test
cd C:\mewbot_dev\mewbot
python setup.py core develop
python setup.py api develop
python setup.py io develop
python setup.py test develop

This seemed to work - the uninstall step for io and test _should_ not be needed.
But, as this is going to be a script, there seemed no reason to not try.
