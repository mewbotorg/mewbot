
## Test linters have installed properly

### 11) First linting

Before we proceed to install mewbot we should check that the linters included in the `requirements-dev.txt` file have properly installed.
They should be, and should be on the path, but it's a good idea to check.

cd to your mewbot folder - for me `C:\mewbot_dev\mewbot` and run the following commands

#### black

To do so, run

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>black src
All done! ✨ 🍰 ✨
15 files left unchanged.
```

(the number of files will probably be different by the time you read this).

#### flake8

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>flake8 src
```

(which should produce no output)

#### mypy

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>mypy src
src\mewbot\ioconfigs\discord_io\output.py:6: error: Cannot find implementation or library stub for module named "mewbot.io"
src\mewbot\ioconfigs\discord_io\input.py:11: error: Cannot find implementation or library stub for module named "mewbot.io"
src\mewbot\ioconfigs\discord_io\input.py:11: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
src\mewbot\ioconfigs\socket_input\input.py:8: error: Cannot find implementation or library stub for module named "mewbot.io"
src\mewbot\ioconfigs\post_input\input.py:21: error: Cannot find implementation or library stub for module named "mewbot.io"
Found 4 errors in 4 files (checked 15 source files)
```

(These errors are to be expected - mewbot is not currently installed in the venv - so the static analysis tools - which are using the venv's python.exe get confused.)
NOTE - The number of files checked should match the number of files which where checked by black.

#### pylint

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>pylint src
```

or

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>pylint
```

(This will probably throw a bunch of errors - we're just testing the `venv` for now).

#### pydocstyle

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>pydocstyle
```

(This _should not_ complain - we're pretty sure we have a `pydocstyle` compliant code base)