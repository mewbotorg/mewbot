
Mewbot has the potential to connect to a _great many_ services.
Potentially hundreds.

As such, if all of them are deployed automatically, then the system may become somewhat hard to handle.
So the individual IOConfigs need to be broken down into separate modules - so the user can install.

There seem to be a number of ways to do this.

### Completely separate modules - no plugin loader system

Additional IOConfigs would be configured as separate packages inheriting from mewbot - which each package would specify as a dependency.
Packages would then be imported and used manually by the user.

#### What does it look like

 - Absolute anarchy. 
 - Call your packages what you want.
 - Install them where you want.
 - Packages probably are not well labelled and you just find them where you can
 - No good ways of detecting all available optional extras and packages - you have to install and customize everything yourself.
 - Perhaps not brilliant for a low code audience.
 - Installation is just pip installing the package and then manually importing from it.

#### Pros

 - Probably the simplest - and cleanest of the bunch.
 - Least likely to exhibit unexpected behavior
 - Easy to develop for - just inherit from mewbot and off you go (note - might be able to extend the registry to do this - but think would need to import to trigger the class creation and so registry code)
 - Flexibility - encourages people to write their own code and load it in as required
 - You can also call your packages whatever you want


#### Cons

 - Quite hard to get things like module discovery for the GUI working - would probably end up reimplementing a fair amount of a plugin system.
 - Fully isolated - so quite hard to comprehensively test (also - the fundamental problem with plugin based projects is that they may drift out of spec... but it's also easier to develop for them)


### Completely separate modules - plugin loader system

Additional IOConfigs would be defined as separate packages - inheriting from mewbot.
However, a plugin system detects the presence of packages and imports them automatically. So they can be detected by the user.

#### What does it look like

 - Using `pluggy` you write a plugin definition and a plugin marker (the latter being far simpler)
 - To access the plugins, once developed and installed, you can generate a plugin manager
 - You then have a number of options for registering plugins with the system
 - You can do it manually - probably this is how to handle the inbuilt classes bundled
 - But it can also scan all installed modules for ones which match patterns - such as "mewbot-*"
 - So you build packages - import the markers to mark your implementation of the plugins as such - then rely on some special sauce in setup.py to set entry points so `pluggy` can load the plugin appropriately
 - Just install the module you've written as normal

#### Pros

 - Fully isolated packages, but discoverable and loadable through the plugin system - so a good compromise.
 - Easier to test than the completely uncoupled system
 - Probably can actually break the main package down - isolate tests e.t.c.
 - Flexibility - but with enough support that we can examine the loaded modules - hopefully with encourage people to actually write plugins.
 - I mean, we can dream!

#### Cons

 - Harder to set up and develop for - pytest (which uses `pluggy` for their plugin system) has a dedicated project which creates the skeletons for new plugins. Probably have to steal that.
 - Still has the difficulties of testing.
 - You need to call your packages something regulr (e.g. something matching the pattern "mewbot-*") for them to be picked up by the loader.

### Optional dependencies

- All code for all the extra components would be included in the main repo.
- But would only load the dependencies required to make them work if those packages are specified.
- Installation would take the form of `python -m pip install mewbot[discordIO]` - which would only install `discord.py` if the user wants it.

#### Pros

 - Easy - can be done straight in setup.py with no additional modules
 - Clunky - might well confuse type checking
 - Testing becomes a lot easier - just include the right dependencies in the dev requirements and off you go.

#### Cons

 - Means that bits of the code may start unexpectedly working when you install other packages that they depend on. Surprise additional functionality does not seem like it would be a good thing.
 - Significant lack of elegance - having to do a bunch of checks at run time. The linters will probably complain.

---

So probably the best compromise is to actually have a plugin system = `pluggy` seems to be a pretty robust system - pytest uses it on the backend - [Pluggy Docs](https://pluggy.readthedocs.io/).
Thus a completely separate module system with a plugin system.

Possibly also some nice hacks to do with the setup.py optional plugin system to allow the user to instruct the system as to which plugins to install.

Note - python provides it's own mechanisms for doing this - [here](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/).

I _think_ I prefer pluggy - it has some features I would feel compelled to build on top of the python mechanism.
No reason not to use both in concert of course.

---

### A rather annoying problem

mewbot - as per the setup instructions - is currently being run by running the setup.py file directly

Something like

```shell
python setup.py develop
```

from the root of the project.

In order to present an example of how the plugins should be created I created a new plugins folder, and, inside it, started populating it with plugins. The first was `mewbot-discord_dice_roller`.
Which just presents a Behavior with a Trigger and Action built in - provides a dice rolling service for Discord.
Nothing very sophisticated.

I wrote the `setup.py` file following the `pluggy` instructions.
Invoking
```shell
python plugins\mewbot-discord_dice_roller\setup.py develop
```

Did not, in fact, produce a working plugin because the venv python interpreter could not find mewbot anymore.
After some experimentation, I determined that running one `setup.py` would break the other and visa-versa.

On the other hand, the command

```shell
python -m pip install --editable ..\mewbot
```

followed by

```shell
python -m pip install --editable plugins\mewbot-discord_dice_roller
```

seemed to work a lot better.
For some reason.
This seems to be the way to canonically install all plugins in a development environment.

As testing the plugin manager requires some plugins to actually be installed, will need to experiment some with how to do that automatically as part of the online tests.
