#!/usr/bin/env python3

from typing import Tuple

import os

from mewbot.plugins.hook_specs import mewbot_dev_hook_impl

# This is the name which will actually show up in the plugin manager.
# Note - this also allows you to extend an existing plugin - just set the name
# of your new plugin to the same as the one you wish to extend.

__mewbot_plugin_name__ = "base"


@mewbot_dev_hook_impl  # type: ignore
def declare_src_locs() -> Tuple[str, ...]:
    """
    If we declare the location of this plugin's source tree then it can be linted.
    :return:
    """
    current_file = __file__
    mewbot_top_level_folder = str(os.path.split(current_file)[0])
    mewbot_src_folder = str(os.path.split(mewbot_top_level_folder)[0])

    return tuple(
        [
            mewbot_src_folder,
        ]
    )


@mewbot_dev_hook_impl  # type: ignore
def declare_example_locs() -> Tuple[str, ...]:
    """
    Declaring the location of the examples contained in the main module.
    :return:
    """
    current_file = __file__
    mewbot_top_level_folder = str(os.path.split(current_file)[0])
    mewbot_src_folder = str(os.path.split(mewbot_top_level_folder)[0])
    mewbot_package_folder = str(os.path.split(mewbot_src_folder)[0])

    return tuple([os.path.join(mewbot_package_folder, "examples")])


# mewbot does not contain its own tests - so declare_test_locs is not defined
# That will happen in the mewbot_tests module
