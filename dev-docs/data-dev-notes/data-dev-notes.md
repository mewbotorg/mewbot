<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

# Typing issues

The main problem with DataSources/DataStores (DSS) is the typing.
Which I'm not sure _can_ be solved.

## 1 - General problems with typing arbitary structures

Adding a conformance function to the DataSource/Store has helped a lot.
(A function which assures that the return is of the type declared when the Data structure is initialized.)
You can use this before return functions, and for data validation on the way in.
Which seems to keep the type checkers (mostly) happy.

Doing this automatically would be nice, but requires some heavy type introspection which seems either quite hard, or
impossible.

It would also (e.g. for Json) be nice to allow arbitrary data structures to be expressed and accessed through stores.
This is, however, extremely difficult to square the circle with type checkers.
I think the best compromise is to build out the base cases, and to try and make the base classes easily extendable.
People can then create custom a DSS for the structure they want to express in json (with some, potentially quite gnarly, 
checking code to validate the structure as it's loaded/accessed/modified by the DSS).

## 2 - Typing structures loaded out of yaml

DSSs are unlike the other components, in that they have more divergent interfaces.
Probably the best way, if an Action/Trigger e.t.c. requires a certain DataStore, is to ship protocols for each of the 
base types of DataStore - people can then use these in place of _specific_ DSSs to make their code more portable.

Just going to have to declare the protocols (which will probably be a generic protocol with a specific type) the DSS
follows when it's declared or used.
(Be nice if it could be included in the yaml in some way, but that's not looking super possible - the yaml would have
to be included in linting and understandable by the type checker. Not easy.)

## 3 - Actually including them in yaml

There seems to be a number of approaches that make sense.

### 1 - DSS defined in a separate yaml block - then available to all components

Something like

```yaml
# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: CC-BY-4.0
# An _absolutely_

kind: DataSource
implementation: mewbot.data.json_data.JsonStringDataSourceListValues
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa00
properties:
  json_string: '[1, 2, 3]'

---

kind: IOConfig
implementation: mewbot.io.discord.DiscordIO
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa01
properties:
  token: "[token goes here]"

---

kind: Behaviour
implementation: mewbot.api.v1.Behaviour
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa02
properties:
  name: 'Echo Inputs'
triggers:
  - kind: Trigger
    implementation: examples.discord_bots.trivial_discord_bot.DiscordTextCommandTrigger
    uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa03
    properties:
      command: "!hello"
conditions: []
actions:
  - kind: Action
    implementation: examples.discord_bots.trivial_discord_bot.DiscordCommandTextResponse
    uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa04
    properties:
      message: "world"

```

The word available in that description is doing quite a lot of heavy lifting.
Does this mean they can _request_ it, or that it is automatically loaded?

In this case, I think _request_ would be better.
However, it does run into a problem of grain of access control.
It'd be good to be able to limit the data stores which an object can access.

### 2 - DSS defined in the yaml block of the component which is going to use it

To me, this doesn't seem elegant.

a) it would require separate logic, handling DSS creation, for each of the components.
b) sharing DSSs between components then becomes somewhat cumbersome. Doable. But annoying.
c) it's not in keeping with how we define components elsewhere

Think this option can be ruled out.

### 3 - DSS defined in its own block - can be loaded into the components which need it by name

Something like

```yaml
# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: CC-BY-4.0
# An _absolutely_

kind: DataSource
name: vals_for_d6
implementation: mewbot.data.json_data.JsonStringDataSourceListValues
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa00
properties:
  json_string: '[1, 2, 3, 4, 5, 6]'

---

kind: IOConfig
implementation: mewbot.io.discord.DiscordIO
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa01
properties:
  token: "[token goes here]"

---

kind: Behaviour
implementation: mewbot.api.v1.Behaviour
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa02
properties:
  name: 'Roll a d6 using a DataStore's internal random method'
triggers:
  - kind: Trigger
    implementation: examples.discord_bots.trivial_discord_bot.DiscordTextCommandTrigger
    uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa03
    properties:
      command: "!dice"
conditions: []
actions:
  - kind: Action
    implementation: examples.data_sources.terrible_dice_roller.RollDiceAction
    uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa04
    properties:
      datasource: vals_for_d6

```

You can tag DataSources and DataStores into any asset you want.
To objects which want to use DSS, they'd have the keywords datasource(s)/datastores(s) added - for either an individual
DSS or a list of them.

Because you declare the DSS _first_ before tagging it in, you will always get the same instance.
Which is helpful for Stores and _should not matter at all_ for Sources.
Which _should_ be immutable.

This seems a (fairly) elegant way of doing things.

Probably going to need a guide to using Data in your bot...
And one for writing new DSSs.

Hey, ho.
We need persistent data - and we need it to be easy as possible.