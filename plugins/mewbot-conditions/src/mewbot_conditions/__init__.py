#!/usr/bin/env python3

from typing import Tuple, Type, Dict

from mewbot.api.v1 import Condition
from mewbot.plugins.hook_specs import mewbot_ext_hook_impl

from .conditions import MondayCondition, NotMondayCondition

__mewbot_plugin_name__ = "extended_conditions"


@mewbot_ext_hook_impl  # type: ignore
def get_condition_classes() -> Dict[str, Tuple[Type[Condition], ...]]:
    """
    Returns the condition classes defined by the plugin module.
    :return:
    """
    return {__mewbot_plugin_name__: tuple([MondayCondition, NotMondayCondition])}
