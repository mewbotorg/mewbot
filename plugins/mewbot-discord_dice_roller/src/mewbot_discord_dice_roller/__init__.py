#!/usr/bin/env python3

from typing import Tuple, Type, Dict

from mewbot.plugins.hook_specs import mewbot_ext_hook_impl

from .triggers import DiscordDiceRollCommandTrigger
from .actions import DiscordRollTextResponse
from .behaviors import DiscordDiceRollerBehavior

# This could also be accomplished by some clever registry hacks
# But it might be better to explicitly declare the classes that should be exposed

__mewbot_plugin_name__ = "discord_dice_roller"



# You have to mark functions within a namespace
# In this case the module itself is going to be the namespace
# (as this might be what the loader needs to automatically pick up the classes)
@mewbot_ext_hook_impl  # type: ignore
def get_trigger_classes() -> Dict[str, Tuple[Type[DiscordDiceRollCommandTrigger], ...]]:
    """
    Return the trigger classes defined in this plugin.
    :return:
    """
    return {__mewbot_plugin_name__: tuple(
        [
            DiscordDiceRollCommandTrigger,
        ]
    )
    }


@mewbot_ext_hook_impl  # type: ignore
def get_action_classes() -> Dict[str, Tuple[Type[DiscordRollTextResponse], ...]]:
    """
    Returns the action classes defined in this plugin.
    :return:
    """
    return {__mewbot_plugin_name__: tuple(
        [
            DiscordRollTextResponse,
        ]
    )
    }


# Todo: Cannot rely on the type system - so automated type checking?
@mewbot_ext_hook_impl  # type: ignore
def get_behavior_classes() -> Dict[str, Tuple[Type[DiscordDiceRollerBehavior], ...]]:
    """
    Returns the behavior classes defined by this plugin.
    :return:
    """
    return {__mewbot_plugin_name__: tuple(
        [
            DiscordDiceRollerBehavior,
        ]
    )
    }
