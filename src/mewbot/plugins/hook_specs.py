#!/use/bin/env python3

"""
pluggy plugins need two things
 - a spec for the implementation
 - a decorator to mark an object in your project as an implementation
This module provides these for a number of mewbot use cases.
(Such as
 - regular information which plugins might offer - such as components
 - development information which plugins might offer
It also provides some guidance - in the spec docstrings - as to how to write
extensions.

"""

from typing import Tuple, Type, Dict, List

import pluggy  # type: ignore

from mewbot.api.v1 import (
    Trigger,
    IOConfig,
    Input,
    Output,
    Condition,
    Action,
    Behaviour,
    InputEvent,
    OutputEvent,
)

# The specification for a hook namespace to provide mewbot components
mewbot_ext_hook_spec = pluggy.HookspecMarker("mewbot")
# The marker which corresponds to that implementation - import to use
# (see examples in plugins folder)
mewbot_ext_hook_impl = pluggy.HookimplMarker("mewbot")


class MewbotPluginSpec:
    """
    Specification for a plugin to provide any known mewbot component(s).
    It's quite possible that a single module will provide multiple additional components
    of the same type - so all the getter methods which returns the contributions for that
    type of component return tuples of that component (thus the get_io_configs method
    will return a tuple of IOConfig classes.
    """

    @mewbot_ext_hook_spec  # type: ignore
    def get_io_config_classes(self) -> Dict[str, Tuple[Type[IOConfig], ...]]:
        """
        Return the IOConfigs defined by the plugin module.
        Note - IOConfig needs to be extended with YAML signature info - though this can also
        be generated from properties.
        Return type is keyed with a str - a category.
        This category is (usually) just the name of the plugin module, but a single module can
        define multiple categories.
        :return:
        """

    @mewbot_ext_hook_spec  # type: ignore
    def get_input_event_classes(self) -> Dict[str, Tuple[Type[InputEvent], ...]]:
        """
        Return all the input classes defined by a plugin.
        These could also be accessed through a plugin's IOConfigs.
        Return type is keyed with a str - a category.
        This category is (usually) just the name of the plugin module, but a single module can
        define multiple categories.
        :return:
        """

    @mewbot_ext_hook_spec  # type: ignore
    def get_input_classes(self) -> Dict[str, Tuple[Type[Input], ...]]:
        """
        Returns the Inputs defined by the plugin module.
        Ideally this should never be used - instead an IOConfig class should be provided
        with a construction method which produces the Inputs/Outputs needed for the IOConfig
        to function.
        However, permitting the option does allow for more flexibility.
        :return:
        """

    @mewbot_ext_hook_spec  # type: ignore
    def get_output_event_classes(self) -> Dict[str, Tuple[Type[OutputEvent], ...]]:
        """
        Reut
        :return:
        """

    @mewbot_ext_hook_spec  # type: ignore
    def get_output_classes(self) -> Dict[str, Tuple[Type[Output], ...]]:
        """
        Returns the Inputs defined by the plugin module.
        Ideally this should never be used - instead an IOConfig class should be provided
        with a construction method which produces the Inputs/Outputs needed for the IOConfig
        to function.
        However, weirdness happens.
        :return:
        """

    @mewbot_ext_hook_spec  # type: ignore
    def get_trigger_classes(self) -> Dict[str, Tuple[Type[Trigger], ...]]:
        """
        Returns the trigger classes defined by the plugin module.
        It's often a good idea - if you're writing a new IOConfig - to include a trigger for
        all the InputEvents it produces.
        :return:
        """

    @mewbot_ext_hook_spec  # type: ignore
    def get_condition_classes(self) -> Dict[str, Tuple[Type[Condition], ...]]:
        """
        Returns the condition classes defined by the plugin module.
        :return:
        """

    @mewbot_ext_hook_spec  # type: ignore
    def get_action_classes(self) -> Dict[str, Tuple[Type[Action], ...]]:
        """
        Returns the action classes defined by the plugin module
        :return:
        """

    @mewbot_ext_hook_spec  # type: ignore
    def get_behavior_classes(self) -> Dict[str, Tuple[Type[Behaviour], ...]]:
        """
        Returns the behavior classes defined by this module.
        Notes - there is current no mechanism to allow you to return pre-made behaviors
        So you can't pass back pre-made classes.
        This shouldn't be too much of a problem - see the examples.
        :return:
        """


# Eventually it should be possible to populate the implementation directly using a registry

# Spec to provide means of providing dev information to mewbot
mewbot_dev_hook_spec = pluggy.HookspecMarker("mewbot_dev")
# The marker which corresponds to that implementation
mewbot_dev_hook_impl = pluggy.HookimplMarker("mewbot_dev")


class MewbotDevPluginSpec:
    """
    There is various information that a plugin might want to provide to mewbot to assist with
    development.
    Such as
     - where its source code is (for linting purposes)
     - where its tests are (so that they can be run as part of the test suite)
    """

    NON_FUNCTION_NAMES = frozenset(
        [
            "__class__",
            "__delattr__",
            "__dict__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__le__",
            "__lt__",
            "__module__",
            "__ne__",
            "__new__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__subclasshook__",
            "__weakref__",
            "NON_FUNCTION_NAMES",
            "validate_function_name",
        ]
    )

    @classmethod
    def validate_function_name(cls, function_name: str) -> bool:
        """
        Check that a function that we want to call in this namespace actually exists.
        Returns True if it does - and so can be called - False otherwise.
        :param function_name:
        :return:
        """
        viable_names = set(dir(cls)) - cls.NON_FUNCTION_NAMES
        return function_name in viable_names

    @mewbot_dev_hook_spec  # type: ignore
    def declare_src_locs(self) -> Tuple[str, ...]:
        """
        Allows the plugin to declare where its src folders are - so they can be linted.
        Should return a tuple of paths to be linted.
        :return:
        """

    @mewbot_dev_hook_spec  # type: ignore
    def declare_test_locs(self) -> Tuple[str, ...]:
        """
        Allows the plugin to declare where its tests are - so they can be included in the main
        test run.
        (Optionally, so they can also be linted)
        :return:
        """

    @mewbot_dev_hook_spec  # type: ignore
    def declare_example_locs(self) -> Tuple[str, ...]:
        """
        Allows a function to declare where it's examples are.
        So they can be included in the unified examples interface.
        (Optionally, so they can also be linted)
        :return:
        """


def gather_dev_paths(target_func: str = "declare_test_locs") -> List[str]:
    """
    Plugins can declare extra paths for the various tools.
    :param target_func: The function to execute from the hooks
                        Must return an iterable of strings
    :return:
    """
    pluggy_manager = pluggy.PluginManager("mewbot_dev")
    pluggy_manager.add_hookspecs(MewbotDevPluginSpec())
    pluggy_manager.load_setuptools_entrypoints("mewbotv1")

    assert MewbotDevPluginSpec.validate_function_name(
        target_func
    ), f"Cannot call function {target_func} - does not exist in the spec!"

    # Load the declared src code paths
    results = getattr(pluggy_manager.hook, target_func)()  # Linter hack
    src_paths: List[str] = []
    for result_tuple in results:
        for path in result_tuple:
            if isinstance(path, str):
                src_paths.append(path)
            else:
                print(f"{path} not  a valid path")

    return src_paths
