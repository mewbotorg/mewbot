
# Plugin dev notes

Notes on creating plugins and extensions for mewbot.

## Plugin writing intro

### Why you might want to write a plugin?

There are two reasons - and two types of plugin you might want to write.

#### 1) Extending mewbot itself

Base mewbot is more a framework than a complete program.
It's designed to take yaml files, load them, and turn them into bots which can interact with the world.
While it does have some basic capabilities, the majority of its capabilities come from plugins
(either plugins already bundled with the program or plugins written for it.)

Thus, if you want to extend the capabilities of the _framework itself_ you probably want to write a **mewbot framework plugin**.

On a technical level this will take the form of a namespace plugin which will use the `mewbot_framework_plugin_template`.

E.g. I would like mewbot to be able to talk to "Insert communications protocol here".
I will write a plugin which will present a new IOConfig in `mewbot.io`

For further information on how to write namespace plugins, please see the python core documentation - [python namespace plugin docs](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/).

#### 2) Creating tools for bots

If, on the other hand, you want to write some tools which bots _themselves_ will use, then you probably want to write a **mewbot bot plugin**.

This would be a plugin for mewbot which does not add to the core module namespace.
It might include detailed Triggers, Conditions and Actions that you will use to build your bot via yaml.

It might even include custom IOConfigs.
Though, if you're going to the effort of writing one, please consider either
1) extending an existing IOConfig with new capabilities
2) writing a framework plugin to expose your IOConfig more broadly.

### Which one should I use?

As a rule of thumb
1) If the plugin components should appear in the core namespace, write a **framework plugin**
2) If the plugin components are to support a specific bot or a collection of bots, then write a **bot plugin**

E.g.

#### Example 1

"I want to allow mewbot to talk to mastadon"

Probably write a **framework** plugin.

In fact, please do!
That would really be very helpful.

Your generic IOConfig will take the form of a namespace plugin.
It will be used by importing it using something like

```python
from mewbot.io.mastadon import MastadonIOConfig
```

#### Example 2

"I've written a discord dice roller! I'd like to distribute it."

Probably write a **bot** plugin.

Structure it how you like.
Use the components by having lines such as 

```yaml
kind: Behaviour
implementation: mewbot_discord_dice_roler.behaviors.DiceRollerBehavior
uuid: aaaaaaaa-aaaa-4aaa-0000-aaaaaaaaaa02
properties:
  name: 'RSS Printer'
triggers:
  - kind: Trigger
    implementation: mewbot.io.common.AllEventTrigger
    uuid: aaaaaaaa-aaaa-4aaa-0000-aaaaaaaaaa03
    properties: { }
  - kind: Trigger
    implementation: mewbot.io.common.AllEventTrigger
    uuid: aaaaaaaa-aaaa-4aaa-0000-aaaaaaaaaa04
    properties: { }
conditions: []
actions:
  - kind: Action
    implementation: mewbot_discord_dice_roller.actions.RollTheDice
    uuid: aaaaaaaa-aaaa-4aaa-0000-aaaaaaaaaa05
    properties: { }

```

(descriptive names are preferred for this sort of plugin as the yaml is intended to be highly human readable).

#### Example 3

"I've written some awesome conditions. I want to distribute them."

You probably want a **bot** plugin.
But, if they are _extremely_ generic, they might be candidates for inclusion in `mewbot.io.common`.
This will, however, be fairly rare.
To keep the core framework as light weight as possible.