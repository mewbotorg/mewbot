#!/usr/bin/env python3
# pylint: disable=duplicate-code
# pylint does not play nice with the requirements of pluggy
# i.e. it's complaining at the declare_test_locs function

from typing import Tuple, Type, Dict

import os

from mewbot.api.v1 import IOConfig, Input, InputEvent
from mewbot.plugins.hook_specs import mewbot_ext_hook_impl
from mewbot.plugins.hook_specs import mewbot_dev_hook_impl

from .io_configs.reddit_password_io import RedditPasswordIO
from .io_configs import RedditRedditorInput, USED_INPUT_EVENTS
from .io_configs.inputs.subreddit import RedditSubredditInput

# This is the name which will actually show up in the plugin manager.
# Note - this also allows you to extend an existing plugin - just set the name
# of your new plugin to the same as the one you wish to extend.
#
__mewbot_plugin_name__ = "reddit"


@mewbot_ext_hook_impl  # type: ignore
def get_io_config_classes() -> Dict[str, Tuple[Type[IOConfig], ...]]:
    """
    Return the IOConfigs defined by this plugin module.
    Note - IOConfig needs to be extended with YAML signature info - though this can also
    be generated from properties.
    :return:
    """
    return {
        __mewbot_plugin_name__: tuple(
            [
                RedditPasswordIO,
            ]
        )
    }


@mewbot_ext_hook_impl  # type: ignore
def get_input_classes() -> Dict[str, Tuple[Type[Input], ...]]:
    """
    Returns the Input classes defined by this plugin.
    In this case, there are two.
    :return:
    """
    return {__mewbot_plugin_name__: tuple([RedditSubredditInput, RedditRedditorInput])}


@mewbot_ext_hook_impl  # type: ignore
def get_input_event_classes() -> Dict[str, Tuple[Type[InputEvent], ...]]:
    """
    Returns all the InputEvent subclasses defined by this plugin.
    :return:
    """
    return {__mewbot_plugin_name__: USED_INPUT_EVENTS}


@mewbot_dev_hook_impl  # type: ignore
def declare_src_locs() -> Tuple[str, ...]:
    """
    If we declare the location of this plugin's source tree then it can be linted.
    :return:
    """
    current_file = __file__
    mewbot_reddit_top_level_folder = str(os.path.split(current_file)[0])
    mewbot_reddit_src_folder = str(os.path.split(mewbot_reddit_top_level_folder)[0])

    return tuple(
        [
            mewbot_reddit_src_folder,
        ]
    )


@mewbot_dev_hook_impl  # type: ignore
def declare_test_locs() -> Tuple[str, ...]:
    """
    If we declare the location of this plugin's tests then they can be included in the main
    test run.
    :return:
    """
    current_file = __file__
    mewbot_reddit_top_level_folder = str(os.path.split(current_file)[0])
    mewbot_reddit_src_folder = str(os.path.split(mewbot_reddit_top_level_folder)[0])
    mewbot_reddit_base_folder = str(os.path.split(mewbot_reddit_src_folder)[0])

    return tuple(
        [
            os.path.join(mewbot_reddit_base_folder, "tests"),
        ]
    )


@mewbot_dev_hook_impl  # type: ignore
def declare_example_locs() -> Tuple[str, ...]:
    """
    Declaring the location of the examples contained in the main module.
    :return:
    """
    current_file = __file__
    mewbot_reddit_top_level_folder = str(os.path.split(current_file)[0])
    mewbot_reddit_src_folder = str(os.path.split(mewbot_reddit_top_level_folder)[0])
    mewbot_reddit_package_folder = str(os.path.split(mewbot_reddit_src_folder)[0])

    return tuple([os.path.join(mewbot_reddit_package_folder, "reddit_examples")])
