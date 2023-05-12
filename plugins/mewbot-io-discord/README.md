<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

# mewbot-io-discord

This module serves two purposes

1) adds discord functionality to mewbot

2) serves as an example of how to configure a mewbot namespace plugin

A mewbot namespace plugin is a plugin used to extend the framework itself.
Mostly in the context of additional IOConfigs.
After installing this module, you'll be able to import the discord IOConfig directly from mewbot.io as follows

```python
from mewbot.io.discord import DiscordIO
```

This is - typically - how new IOConfigs - interfaces to allow mewbot to talk to more protocols - should be written.
