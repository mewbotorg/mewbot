#!/usr/bin/env python3
# pylint: disable=duplicate-code
# this is an example - duplication for emphasis is desirable

from __future__ import annotations

from typing import Any, Dict, Set, Type

import logging

from mewbot.api.v1 import Trigger, Action
from mewbot.core import InputEvent, OutputEvent, OutputQueue
from mewbot.io.discord import DiscordMessageCreationEvent, DiscordOutputEvent


class DiscordDiceRollCommandTrigger(Trigger):
    """
    Nothing fancy - just fires every time a DiscordMessageCreationEvent starts with the text "!roll"
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        return {DiscordMessageCreationEvent}

    def matches(self, event: InputEvent) -> bool:
        if not isinstance(event, DiscordMessageCreationEvent):
            return False

        return event.text.startswith("!roll")
