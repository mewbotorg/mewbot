
## prepare venvs

Perhaps for all the versions of mewbot we're targeting.
Perhaps just for `3.9` - it's sorta up to you.

A `venv` is a `virtual environment` - a copy of your python interpreter which can operate independently of the installed python.
It's all contained in a single folder - which can be removed and recreated if anything goes awry.

### 7) Create a mewbot venv

`venvs` for project development tend to be a good idea.
If nothing else, it makes it less painful if you need to remove the environment entirely because something has gone wrong.

This is also quite a useful feature - as it allows you to test the installation process more easily.
Setting up a dev environment again to test everything is working is a lot easier if doing it means you don't have to wipe out your entire python install.

Put the venv wherever you like - I put mine in `C:\mewbot_dev\mewbot_venv` but, as has probably become apparent, I don't care about polluting the root of my C drive much at all.

Open a cmd prompt and create the venv with

```shell
C:\Users\[YOUR WINDOWS USERNAME]>python -m venv C:\mewbot_dev\mewbot_venv
```

This will only work if you have `python` on the path.

(Note - you can do this from any folder.)

If you haven't, then just use the full path to your python install. e.g.

```shell
C:\Users\[YOUR WINDOWS USERNAME]>C:\python310\python -m venv C:\mewbot_dev\mewbot_venv
```

or just cd into the python folder and run

```shell
C:\python310>python -m venv C:\mewbot_dev\mewbot_venv
```

(With the dst path where ever you want your venv to go).

### 8) Optional - BUT HIGHLY RECOMMENDED - Using doskey to make shortcuts for activating the venv

As above, when we set up doskey, we can use the same method to add arbitrary shortcuts.
In particular, you can use this to streamline the process of activating the `venv` for when you want to do development work with mewbot.

(adapted from [here][2])

If you have already done the steps above - to establish a command precall file - to set up doskey, skip straight to adding new commands to your `.bat` file.
If not, follow the instructions below

1) Firstly, define a list of the alias you want to establish.
2) Then create a .bat file containing those commands.
3) Mine just contained, for the moment
     doskey activate_mewbot_venv=C:\mewbot_dev\mewbot_venv\Scripts\activate
4) Open regedit and navigate to "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Command Processor"
5) Create a new, string variable. Call it "AutoRun" - note the capitalisation - and value it with the absolute path to the .bat file you previously created.
      (I put mine inside my python folder for convenience. But you could put yours anywhere really).
6) Close all open terminals.
7) Test functionality by opening a new cmd prompt and typing "activate_mewbot_venv" - the venv should activate, which should be reflected in the command prompt.
8) Add new commands to the .bat file freely.


If you want to stop the commands in this file being printed to the terminal every time it's run - i.e. every time the terminal is opened, you could do something like this

```shell
@echo off
doskey activate_mewbot_venv=C:\mewbot_dev\mewbot_venv\Scripts\activate
:END
```

which will suppress printing.
If you have used doskey above to get python on the path, just put the command `doskey activate_mewbot_venv=C:\mewbot_dev\mewbot_venv\Scripts\activate` inside the `@echo off` and `:END` enviroments.

(Note - `$*` is _not_ needed on this line. This script does not need command line arguments passed to it)

For more options with `doskey`, see

https://stackoverflow.com/questions/20530996/aliases-in-windows-command-prompt

### 9) Optional - repeat the process with other versions of python

Now you know how to create a `venv`, you could do the same with other versions of python to have more of them on hand for testing purposes.

My command precall file, at this stage of the install process, ended up looking like this

```shell
@echo off
doskey activate_mewbot_venv=C:\mewbot_dev\mewbot_venv_39\Scripts\activate
doskey activate_mewbot_venv_39=C:\mewbot_dev\mewbot_venv_39\Scripts\activate
doskey activate_mewbot_venv_310=C:\mewbot_dev\mewbot_venv_310\Scripts\activate
doskey activate_mewbot_venv_311=C:\mewbot_dev\mewbot_venv_311\Scripts\activate
DOSKEY python3 = C:\\Python310\\python.exe $*
DOSKEY ls=dir /B $*
:END
```

With `venvs` for pythons `3.9`, `3.10` and `3.11`.

This allows me to now, from where ever I am on the system, activate the venv with "activate_mewbot_venv" ... deactivation is left as an exercise to the reader.

Once your venv is activated, then your command prompt should become something like

```shell
(mewbot_venv) C:\mewbot_dev\mewbot_venv\Scripts>
```

(again, assuming you're using the same paths as I am).


Once you have your venv, it is advisable to check you're running off the executable you think you are.

Invoking the python interpreter and checking the executable path is usually a good idea - doing something like.

```shell
C:\Users\mewbot_demo_account>activate_mewbot_venv
(mewbot_venv) C:\Users\mewbot_demo_account>python
Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 19:00:18) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> sys.executable
'C:\\mewbot_dev\\mewbot_venv\\Scripts\\python.exe'
```

Which confirms the executable is where and what we expect.

NOTE - Once the venv is active, a call to `python` should always invoke the venv python interpreter - no matter what your environment was before the venv was activated.

If you have another version of python on your path and, as a consequence, you were using the full path to the python instance you wanted to use for mewbot dev, this should no longer be necessary.
This is why adding python to the path is not really required - you can get around it by using `venvs`.

### 10) Optional - Add paths to the venv(s) for easier import of other modules

A useful tool is the ability to add arbitrary paths to the places the python interpreter in the venv can import from.

This is not currently needed for any steps in this process, but is a useful tool mentioned here for completeness.
(We used it in the past and might do so again in the future).

1) Once you've got a `venv` running locate it's `site-packages` folder.
2) To do this, invoke `python` and type `import sys` and `print(sys.executable)`. 
       The site packages folder should be in the same folder as the executable.
3) Add a txt file with the extension `.pth` to it.
4) Add a list of paths to that file. One per line.
5) The `venv` interpreter should now be able to import modules from those files

(You can use this method as an alternative to installing mewbot in the `venv` - if you don't want to do that for some reason.
Simply add a line to the file - something like `C:\mewbot_dev\mewbot\src`.
Naturally, this will depend on where you put your mewbot development files.
A reason as to why you'd prefer this to installing the module in the `venv` does not, immediately, occur.
But there might be one.)
