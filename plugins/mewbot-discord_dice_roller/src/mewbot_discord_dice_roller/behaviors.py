#!/usr/bin/env python3

from typing import Any

from mewbot.api.v1 import Behaviour

from .triggers import DiscordDiceRollCommandTrigger
from .actions import DiscordRollTextResponse


class DiscordDiceRollerBehavior(Behaviour):
    """
    Dice rolling behavior which automatically includes the triggers and actions
     - DiscordRollCommandTrigger
     - DiscordRollTextResponse
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Adding the trigger and action to the Behavior
        self.add(DiscordDiceRollCommandTrigger())
        self.add(DiscordRollTextResponse())
