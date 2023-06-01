
# mewbot-discord_dice_roller

## Introduction

This project serves a number of purposes.

1) it is an example of how to write plugins for mewbot.

(In particular, how to write a plugin to provide components for a mewbot bot - a `mewbot-bot` plugin.

This is not intended to extend mewbot itself - it's a collection of utility methods.
As such, it will not be included in the mewbot namespace.

If you want that, you want to write a `mewbot-namespace` plugin).

2) it's a fairly capable dice roller plugin which you can adapt - pretty quickly - to almost any text based input method.

## Project contents

This project provides examples of

1) Defining a Trigger, Action and Behavior which can be detected and loaded by the registry.
2) The basic `setup.py` file that you will need to include in your external projects to have them recognized as mewbot plugins.

Conceptually, this is very simple.

The registry - located in `mewbot.api.registry` stores all instances of the various mewbot components which inherit from the base classes in the api.
All you need to register your class is to inherit from the `mewbot.api.v1` and include a special entry point in the `setup.py` file.

This allows different bots to use their components - and for them to be made available through the GUI.

## Ho do I use these components?

There are two ways to do this

1) Import the components directly from the `mewbot_discord_dice_roller` module
2) Access them through the registry

Which of these you use is up to you!

Included in this module is two examples - one for each method.
