<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

## Does mypy silently fail on the remote?

It might.

When I'm running `lint.sh` locally on a Windows 10 testing system, I'm getting output which looks like this

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>sh tools/lint
python3 could not be found
You may be on windows - trying with python not python3
NOTE - This may result in you using an unexpected version of python!
All done! ✨ 🍰 ✨
37 files left unchanged.
There are no .py[i] files in directory 'C:\mewbot_dev\mewbot\plugins\mewbot-client_for_reddit\tests'

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

C:\mewbot_dev\mewbot\src\mewbot\tools\preflight.py:1 at module level:
        D100: Missing docstring in public module
```

(the `pydocstyle` error is not relevant).

However, when I run `mypy` directly, I get

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>mypy src
Success: no issues found in 23 source files
```

So it works on the command line, but not through the tool.

Perusing the `mewbot.tools.lint` code, I'm _fairly_ sure that - what might be happening - is that the tool could - or could not - fail to run on remote.
It would then produce the error message

```shell
There are no .py[i] files in directory 'C:\mewbot_dev\mewbot\plugins\mewbot-client_for_reddit\tests'
```

which is not expected, and so would not be caught.
So the tool can silently fail.
This is not ideal.
Resolution - add explicit failure if running in is_ci mode and the error code is non zero.

I'm _fairly_ sure, as a secondary issue, the error message is unhelpful.
Removing the named folder just causes it to name a different folder.

Similar issues

https://github.com/matangover/mypy-vscode/issues/16 - (root cause - folder called `types` - TODO - Add check to tools for folder called `types`? Not currently one present for us)

### Debug

#### Is this an actual problem?

Probably not currently - `mypy` is passing on the command line, after all.
But it needs to be investigated.

Will introduce deliberate error to typing right before I pull request this.
If it is failing silently, I can start proper debug.
If not - all for the good!

Either way, will institute check to see if `mypy` starts silently failing in the future.
Probably checking the output for the bad error message?

#### Removing the `.mypy_cache` from the root of the repo

In the vague hope it'll improve things...

It did not.

#### Removing `*.egg-info` folders from `src`

This might be causing some confusion.

It was not. This did nothing.

#### Solution

Turns out - entire thing _was actually_ caused by setting `mypy` on empty folders - folders I did not think where empty but, actually, where.
Embarrassing!
(What had happened is - I'd changed branches - which had generated some empty folders.
What confused me was the problem appeared intermittent - in fact, it ws showing up every time I changes branches between the two I was actively working on.
The apparent complexity was just a red herring.
The mypy error message was accurate.
).

