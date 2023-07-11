#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
This Behavior brings all the components for the Discord Dice roller together in one place.
"""


from typing import Any

from mewbot.api.v1 import Behaviour

from .actions import DiscordRollTextResponse
from .triggers import DiscordDiceRollCommandTrigger


class DiscordDiceRollerBehavior(Behaviour):
    """
    Dice rolling behavior which automatically includes the needed triggers and actions.

    These are
     - DiscordRollCommandTrigger
     - DiscordRollTextResponse
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Passthrough to the super - which does the actual init work.

        Then adds the dice roller trigger and action.
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        # Adding the trigger and action to the Behavior
        self.add(DiscordDiceRollCommandTrigger())
        self.add(DiscordRollTextResponse())

    def __str__(self) -> str:
        """
        String representation of the behavior.

        :return:
        """
        return (
            f"DiscordDiceRollerBehavior - "
            f"with actions {self.actions} - "
            f"with triggers {self.triggers}"
        )
