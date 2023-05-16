#!/usr/bin/env python3
# pylint: disable=duplicate-code
# this is an example - duplication for emphasis is desirable

"""
Triggers every time a discord message is created.
"""

from __future__ import annotations

from typing import Set, Type

from mewbot.api.v1 import Trigger
from mewbot.core import InputEvent
from mewbot.io.discord import DiscordMessageCreationEvent


class DiscordDiceRollCommandTrigger(Trigger):
    """
    Fires every time a DiscordMessageCreationEvent has text that starts with "!roll".
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        Triggers off all DiscordMessageCreationEvents.

        :return:
        """
        return {DiscordMessageCreationEvent}

    def matches(self, event: InputEvent) -> bool:
        """
        Matches all DiscordMessageCreationEvent with the starting keyword !roll.

        :param event:
        :return:
        """

        if not isinstance(event, DiscordMessageCreationEvent):
            return False

        print(f"In matches with {event=}")

        return event.text.startswith("!roll")
