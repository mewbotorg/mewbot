#!/usr/bin/env python3

from typing import Tuple, Type, Dict

import os

from mewbot.api.v1 import Condition
from mewbot.plugins.hook_specs import mewbot_ext_hook_impl, mewbot_dev_hook_impl

from .conditions import MondayCondition, NotMondayCondition

__mewbot_plugin_name__ = "extended_conditions"


@mewbot_ext_hook_impl  # type: ignore
def get_condition_classes() -> Dict[str, Tuple[Type[Condition], ...]]:
    """
    Returns the condition classes defined by the plugin module.
    :return:
    """
    return {__mewbot_plugin_name__: tuple([MondayCondition, NotMondayCondition])}


@mewbot_dev_hook_impl  # type: ignore
def declare_src_locs() -> Tuple[str, ...]:
    """
    If we declare the location of this plugin's source tree then it can be linted.
    :return:
    """
    return tuple(
        [
            str(os.path.split(str(os.path.split(__file__)[0]))[0]),
        ]
    )
