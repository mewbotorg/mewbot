#!/use/bin/env python3

"""
Manages plugins known to the system.
This will - probably - become a part of the registry.
"""

from typing import List, Tuple, Type, Dict

import logging

import pluggy  # type: ignore

from mewbot.api.v1 import (
    IOConfig,
    Input,
    Output,
    Trigger,
    Condition,
    Action,
    Behaviour,
    Component,
)
from mewbot.plugins.hook_specs import MewbotPluginSpec


class PluginManager:
    """
    Responsible for managing and controlling the individual plugins which
    can be loaded into mewbot.
    """

    _logger: logging.Logger

    _pluggy_pm: pluggy.PluginManager

    def __init__(self) -> None:

        self._logger = logging.getLogger(__name__ + "DiscordInput")

        self.setup_pluggy_plugin_manager()

    def setup_pluggy_plugin_manager(self) -> None:
        """
        Setup the plugin manager
        :return:
        """
        self._pluggy_pm = pluggy.PluginManager("mewbot")
        self._pluggy_pm.add_hookspecs(MewbotPluginSpec())
        self._pluggy_pm.load_setuptools_entrypoints("mewbotv1")  # This might not be needed

    def get_available_plugin_names(self) -> List[str]:
        """
        Returns a list of the names of all currently installed plugins.
        :return:
        """
        return [po[0] for po in self._pluggy_pm.list_name_plugin()]

    def get_available_plugin_classes(self) -> Dict[str, List[str]]:
        """
        Returns a dict keyed with the type of class available and valued with a list of the
        available types of that class.
        :return:
        """
        rtn_dict: Dict[str, List[str]] = {}

        rtn_dict["IOConfigs"] = [
            self._get_plugin_component_name(pcls)
            for pcls in self.get_plugin_io_config_classes()
        ]
        rtn_dict["Inputs"] = [pcls.__name__ for pcls in self.get_plugin_input_classes()]
        rtn_dict["Outputs"] = [pcls.__name__ for pcls in self.get_plugin_output_classes()]
        rtn_dict["Triggers"] = [pcls.__name__ for pcls in self.get_plugin_trigger_classes()]
        rtn_dict["Conditions"] = [
            pcls.__name__ for pcls in self.get_plugin_condition_classes()
        ]
        rtn_dict["Actions"] = [pcls.__name__ for pcls in self.get_plugin_action_classes()]
        rtn_dict["Behaviors"] = [pcls.__name__ for pcls in self.get_plugin_behavior_classes()]

        return rtn_dict

    @staticmethod
    def _get_plugin_component_name(target_cls: Type[Component]) -> str:
        """
        Take a component presented by a plugin and extract it's name.
        Tries for a human readable name, and falls back to __name__ if not present.
        # Todo: Want both the human readable name and __name__ to work
        # Todo: C;ash checking and warning if names are clashing
        :return:
        """
        if hasattr(target_cls, "display_name"):
            result = getattr(
                target_cls,
                "display_name",
            )
            if isinstance(result, str):
                return result
        return target_cls.__name__

    # These methods are not very DRY - but the type checking was problematic if they were
    # replaced with a generic class
    # It was possible - just annoying

    def get_plugin_io_config_classes(self) -> Tuple[Type[IOConfig], ...]:
        """
        Returns the available IOConfig classes declared by all the plugins as a list.
        :return:
        """
        results = getattr(self._pluggy_pm.hook, "get_io_config_classes")()  # Linter hack

        rtn_list: List[Type[IOConfig]] = []
        for result_dict in results:
            for plugin_category in result_dict:
                result_tuple = result_dict[plugin_category]
                for io_config_class in result_tuple:
                    if issubclass(io_config_class, IOConfig):
                        rtn_list.append(io_config_class)
                    else:
                        self._logger.warning(
                            "Bad class from plugin - expected IOConfig class - got %s",
                            io_config_class,
                        )
                        continue

        return tuple(rn for rn in rtn_list)

        # This would be the best way to do this, but the type checks do not like it
        # return tuple(list(itertools.chain(*results)))

    def get_plugin_input_classes(self) -> Tuple[Type[Input], ...]:
        """
        Returns the available IOConfig classes declared by all the plugins as a list.
        :return:
        """
        results = getattr(self._pluggy_pm.hook, "get_input_classes")()

        rtn_list: List[Type[Input]] = []
        for result_dict in results:
            for plugin_category in result_dict:
                result_tuple = result_dict[plugin_category]
                for input_class in result_tuple:
                    if issubclass(input_class, Input):
                        rtn_list.append(input_class)
                    else:
                        self._logger.warning(
                            "Bad class from plugin - expected Input class - got %s",
                            input_class,
                        )
                        continue

        return tuple(rn for rn in rtn_list)

    def get_plugin_output_classes(self) -> Tuple[Type[Output], ...]:
        """
        Returns the available IOConfig classes declared by all the plugins as a list.
        :return:
        """
        results = getattr(self._pluggy_pm.hook, "get_output_classes")()

        rtn_list: List[Type[Output]] = []
        for result_dict in results:
            for plugin_category in result_dict:
                result_tuple = result_dict[plugin_category]
                for output_class in result_tuple:
                    if issubclass(output_class, Output):
                        rtn_list.append(output_class)
                    else:
                        self._logger.warning(
                            "Bad class from plugin - expected Output class - got %s",
                            output_class,
                        )
                        continue

        return tuple(rn for rn in rtn_list)

    def get_trigger(self, trigger_name: str) -> Type[Trigger]:
        """
        Return a specified condition by name.
        :param trigger_name:
        :return:
        """
        cand_class = None
        for bh_clas in self.get_plugin_trigger_classes():
            if self._get_plugin_component_name(bh_clas) == trigger_name:
                cand_class = bh_clas
                break

        if cand_class is None:
            self._logger.warning(
                "Searched for an Action, %s, which has not been loaded", trigger_name
            )
            raise ModuleNotFoundError(f"Cannot find Action {trigger_name}")

        return cand_class

    def get_plugin_trigger_classes(self) -> Tuple[Type[Trigger], ...]:
        """
        Returns the available Trigger classes declared by all the plugins as a list.
        :return:
        """
        results = getattr(self._pluggy_pm.hook, "get_trigger_classes")()

        rtn_list: List[Type[Trigger]] = []
        for result_dict in results:
            for plugin_category in result_dict:
                result_tuple = result_dict[plugin_category]
                for trigger_class in result_tuple:
                    if issubclass(trigger_class, Trigger):
                        rtn_list.append(trigger_class)
                    else:
                        self._logger.warning(
                            "Bad class from plugin - expected Trigger class - got %s",
                            trigger_class,
                        )
                        continue

        return tuple(rn for rn in rtn_list)

    def get_condition(self, condition_name: str) -> Type[Condition]:
        """
        Return a specified condition by name.
        :param condition_name:
        :return:
        """
        cand_class = None
        for bh_clas in self.get_plugin_condition_classes():
            if self._get_plugin_component_name(bh_clas) == condition_name:
                cand_class = bh_clas
                break

        if cand_class is None:
            self._logger.warning(
                "Searched for an Action, %s, which has not been loaded", condition_name
            )
            raise ModuleNotFoundError(f"Cannot find Action {condition_name}")

        return cand_class

    def get_plugin_condition_classes(self) -> Tuple[Type[Condition], ...]:
        """
        Returns the available Condition classes declared by all the plugins as a list.
        :return:
        """
        results = getattr(self._pluggy_pm.hook, "get_condition_classes")()

        rtn_list: List[Type[Condition]] = []
        for result_dict in results:
            for plugin_category in result_dict:
                result_tuple = result_dict[plugin_category]
                for condition_class in result_tuple:
                    # Can't rely on the plugins output - so have to do type validation here
                    # This has to occur in a typed context for the linters
                    if issubclass(condition_class, Condition):
                        rtn_list.append(condition_class)
                    else:
                        self._logger.warning(
                            "Bad class from plugin - expected Condition class - got %s",
                            condition_class,
                        )
                        continue

        return tuple(rn for rn in rtn_list)

    def get_action(self, action_name: str) -> Type[Action]:
        """
        Return a specified action by name.
        :param action_name:
        :return:
        """
        cand_class = None
        for bh_clas in self.get_plugin_action_classes():
            if self._get_plugin_component_name(bh_clas) == action_name:
                cand_class = bh_clas
                break

        if cand_class is None:
            self._logger.warning(
                "Searched for an Action, %s, which has not been loaded", action_name
            )
            raise ModuleNotFoundError(f"Cannot find Action {action_name}")

        return cand_class

    def get_plugin_action_classes(self) -> Tuple[Type[Action], ...]:
        """
        Returns the available Condition classes declared by all the plugins as a list.
        :return:
        """
        results = getattr(self._pluggy_pm.hook, "get_action_classes")()

        rtn_list: List[Type[Action]] = []
        for result_dict in results:
            for plugin_category in result_dict:
                result_tuple = result_dict[plugin_category]
                for action_class in result_tuple:
                    if issubclass(action_class, Action):
                        rtn_list.append(action_class)
                    else:
                        self._logger.warning(
                            "Bad class from plugin - expected Action class - got %s",
                            action_class,
                        )
                        continue

        return tuple(rn for rn in rtn_list)

    def get_behavior(self, behavior_name: str) -> Type[Behaviour]:
        """
        Return a specified behavior by name.
        :param behavior_name:
        :return:
        """
        cand_class = None
        for bh_clas in self.get_plugin_behavior_classes():
            if self._get_plugin_component_name(bh_clas) == behavior_name:
                cand_class = bh_clas
                break

        if cand_class is None:
            self._logger.warning(
                "Searched for a Behavior, %s, which has not been loaded", behavior_name
            )
            raise ModuleNotFoundError(f"Cannot find Behavior {behavior_name}")

        return cand_class

    def get_plugin_behavior_classes(self) -> Tuple[Type[Behaviour], ...]:
        """
        Returns the available Behavior classes declared by all the plugins as a tuple.
        :return:
        """
        results = getattr(self._pluggy_pm.hook, "get_behavior_classes")()

        rtn_list: List[Type[Behaviour]] = []
        for result_dict in results:
            for plugin_category in result_dict:
                result_tuple = result_dict[plugin_category]
                for condition_class in result_tuple:
                    if issubclass(condition_class, Behaviour):
                        rtn_list.append(condition_class)
                    else:
                        self._logger.warning(
                            "Bad class from plugin - expected Behavior class - got %s",
                            condition_class,
                        )
                        continue

        return tuple(rn for rn in rtn_list)
