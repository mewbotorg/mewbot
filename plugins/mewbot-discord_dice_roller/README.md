This project serves a number of purposes.

Firstly - it is an example of how to write plugins for mewbot.

Secondly - it's a fairly capable dice roller plugin which you can adapt - pretty quickly - to almost any text based input method.

This project provides examples of
1) Defining a Trigger as a plugin
2) Defining an Action as a plugin
3) Defining a behavior as a plugin
4) The basic setup.py file that you will need to include in your external projects to have they recognized as mewbot plugins

The corresponding example in examples/discord_bots demonstrates three ways to use this plugin
1) Directly importing the Behavior
2) Registering it manually with the plugin manager then accessing it through the plugin manager
3) Allowing the plugin manager to introspect the installed modules to find it - then load it from the plugin manager

(Plugin discovery uses entry points to discover and load modules - see [python entry points explanation](https://packaging.python.org/en/latest/specifications/entry-points/).
mewbot uses pluggy to provide plugin services.
)

These should represent the three ways that you might ever want to include a plugin into the system.
We encourage you to use the plugin_manager - quite a lot of other stuff looks to it to populate - it should be considered the definitive way to include and use a plugin in mewbot.

If you are considering building a mewbot plugin
 - Firstly - thank you
 - Secondly - it might be helpful for you to run `mewbot make_new_plugin` and follow the onscreen instructions. This should take care of most of the annoying details of setting up a template project ready for you to add code.
 - Thirdly - when copying the example, be careful about the use of "-" and "_" - both have to be used in confusing and slightly different ways.


