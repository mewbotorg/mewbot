<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

## The testing script/linting scripts pass locally but fail remotely when pushed to github

### Are you running the right version of python?

GitHub - when running a testing or linting script - shows the version of python it is running under.
When looks at these issues, check what version of python you are using (`python --version`).
If the error shows for a different version of python, try again using a matching version of python. 

Note: we generally recommend developing mewbot with the lowest version of python we target (currently `3.10`).
This prevents accidentally developing using features that do not exist in all targeted versions. 

## I'm making changes to the mewbot files, and they're not showing up

Probably you have done something to get two separate copies of `mewbot` in different places.
There are a number of ways this could have happened.

#### You installed `mewbot` with the wrong mode passed to `setup.py`

If you installed `mewbot` using `setup.py` - the recommended method - then you might have run

```shell
(mewbot_venv) C:\mewbot_dev>python setup.py install
```

Instead of

```shell
(mewbot_venv) C:\mewbot_dev>python setup.py develop
```

To disastrous - or at least annoying - effect.

`develop` tells `pip` to leave the files `setup.py` is pointed at in their original place.
It does something behind the scenes to register them as the canonical place files for that module are stored.
So changing these files also changes the module file.

It will also register the module with pip - so pip will consider the requirement `mewbot` satisfied if it appears in another `requirements.txt` file.
This can be particularly useful when installing plugins.

`install`,on the other hand, copies the files into `site_packages`.
So local changes will not be registered unless you run `python setup.py install` again.
Which will overwrite those copied files.

#### You're using path manipulation to "install" mewbot, and you've run `setup.py` from a plugin

One of the disadvantages of getting the `mewbot` code on the path with a path hack is that it can deeply confuse pip.
pip maintains an internal database of the modules it's installed.
When it tries to satisfy a requirement, it'll search that database and if it fails to find it, install it from pypi.
It will not check to see if a module matching that requirement is on the path.

As a consequence of this, unless you install `mewbot` through pip, it might try and load `mewbot` from pypi instead of using your local copy.

In either even
 - uninstalling `mewbot` using pip 
 - the installing pip using `python setup.py install`
_may_ fix the issue.