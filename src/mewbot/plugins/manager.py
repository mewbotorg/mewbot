#!/use/bin/env python3

"""
Manages plugins known to the system.
This will - probably - become a part of the registry.
"""

from typing import List, Tuple, Type, Dict, TypeVar, overload, Optional

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


T = TypeVar("T")


class PluginManager:
    """
    Responsible for managing and controlling the individual plugins which
    can be loaded into mewbot.
    """

    # pylint: disable=too-many-public-methods

    _logger: logging.Logger

    _pluggy_pm: pluggy.PluginManager

    def __init__(self) -> None:

        self._logger = logging.getLogger(__name__ + ":PluginManager")

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

    def get_all_available_plugin_class_names(self) -> Dict[str, List[str]]:
        """
        Returns a dict keyed with the type of class available and valued with a list of the
        available types of that class.
        :return:
        """
        rtn_dict: Dict[str, List[str]] = {}

        io_configs = self.get_all_plugin_io_config_classes()
        rtn_dict["IOConfigs"] = [self._get_plugin_component_name(pcls) for pcls in io_configs]
        rtn_dict["Inputs"] = [pcls.__name__ for pcls in self.get_all_plugin_input_classes()]
        rtn_dict["Outputs"] = [pcls.__name__ for pcls in self.get_all_plugin_output_classes()]
        rtn_dict["Triggers"] = [
            pcls.__name__ for pcls in self.get_all_plugin_trigger_classes()
        ]
        rtn_dict["Conditions"] = [
            pcls.__name__ for pcls in self.get_all_plugin_condition_classes()
        ]
        rtn_dict["Actions"] = [pcls.__name__ for pcls in self.get_all_plugin_action_classes()]
        rtn_dict["Behaviors"] = [
            pcls.__name__ for pcls in self.get_all_plugin_behavior_classes()
        ]

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

    @overload
    def _generic_get_all_plugin_classes(
        self, target_func: str, target_class: Type[T]
    ) -> Tuple[Type[T], ...]:
        """
        Is this solution aggressively stupid? Yes.
        Does it satisfy mypy and pylint at the same time? Also. Yes.
        :param target_func:
        :param target_class:
        :return:
        """
        return self._generic_get_all_plugin_classes(target_func, target_class)

    @overload
    def _generic_get_all_plugin_classes(
        self, target_func: str, target_class: type
    ) -> Tuple[Type[T], ...]:
        """
        Originally there was a problem with mypy - in that it was demanding that classes passed in
        for comparison be concrete rather than abstract.
        (https://github.com/python/mypy/issues/4717).
        These function definitions force it to consider the classes as concrete rather than
        abstract.
        However, they also confused pylint as to the return values if their body was empty.
        Which it was defaulting to assuming where not iterables - hence the specified return.
        :param target_func:
        :param target_class:
        :return:
        """
        return self._generic_get_all_plugin_classes(target_func, target_class)

    def _generic_get_all_plugin_classes(
        self, target_func: str, target_class: Type[T]
    ) -> Tuple[Type[T], ...]:
        """
        Return the requested classes from
        :param target_func:
        :param target_class:
        :return:
        """
        results = getattr(self._pluggy_pm.hook, target_func)()  # Linter hack

        rtn_list: List[Type[T]] = []
        for result_dict in results:
            for plugin_category in result_dict:
                result_tuple = result_dict[plugin_category]
                for cand_class in result_tuple:
                    if issubclass(cand_class, target_class):
                        rtn_list.append(cand_class)
                    else:
                        self._logger.warning(
                            "Bad class from plugin - expected %s class - got %s",
                            target_class,
                            cand_class,
                        )
                        continue

        return tuple(rn for rn in rtn_list)

        # This would be the best way to do this, but the type checks do not like it
        # return tuple(list(itertools.chain(*results)))

    @overload
    def _generic_get_classified_plugin_classes(
        self, target_func: str, target_class: Type[T]
    ) -> Dict[str, Tuple[Type[T], ...]]:
        """
        Is this solution aggressively stupid? Yes.
        Does it satisfy mypy and pylint at the same time? Also. Yes.
        :param target_func:
        :param target_class:
        :return:
        """
        return self._generic_get_classified_plugin_classes(target_func, target_class)

    @overload
    def _generic_get_classified_plugin_classes(
        self, target_func: str, target_class: type
    ) -> Dict[str, Tuple[Type[T], ...]]:
        """
        Originally there was a problem with mypy - in that it was demanding that classes passed in
        for comparison be concrete rather than abstract.
        (https://github.com/python/mypy/issues/4717).
        These function definitions force it to consider the classes as concrete rather than
        abstract.
        However, they also confused pylint as to the return values if their body was empty.
        Which it was defaulting to assuming where not iterables - hence the specified return.
        :param target_func:
        :param target_class:
        :return:
        """
        return self._generic_get_classified_plugin_classes(target_func, target_class)

    def _generic_get_classified_plugin_classes(
        self, target_func: str, target_class: Type[T]
    ) -> Dict[str, Tuple[Type[T], ...]]:
        """
        Return a dictionary keyed with the declared category of the object and valued with a list
        of classes of that type.
        :param target_func:
        :param target_class:
        :return:
        """
        results = getattr(self._pluggy_pm.hook, target_func)()  # Linter hack

        tmp_dict: Dict[str, List[Type[T]]] = {}
        for result_dict in results:
            # This returns a dict keyed with the category and valued by the contributions to it
            for plugin_category in result_dict:
                result_tuple = result_dict[plugin_category]
                rtn_list: List[Type[T]] = []
                for cand_class in result_tuple:
                    if issubclass(cand_class, target_class):
                        rtn_list.append(cand_class)
                    else:
                        self._logger.warning(
                            "Bad class from plugin - expected IOConfig class - got %s",
                            cand_class,
                        )
                        continue
                tmp_dict.update({plugin_category: rtn_list})

        return dict((cls_clasf, tuple(cls_vals)) for cls_clasf, cls_vals in tmp_dict.items())

    # Order of the overloads seems to be important
    @overload
    def _generic_get_plugin_class(
        self, getter_func: str, target_class_name: str, target_class: Type[T]
    ) -> Type[T]:
        return self._generic_get_plugin_class(getter_func, target_class_name, target_class)

    @overload
    def _generic_get_plugin_class(
        self, getter_func: str, target_class_name: str, target_class: type
    ) -> Type[T]:
        return self._generic_get_plugin_class(getter_func, target_class_name, target_class)

    def _generic_get_plugin_class(
        self, getter_func: str, target_class_name: str, target_class: Type[T]
    ) -> Type[T]:
        """
        Generic to
        :param getter_func:
        :param target_class_name:
        :param target_class:
        :return:
        """
        cand_class: Optional[Type[T]] = None
        for bh_clas in getattr(self, getter_func)():
            if self._get_plugin_component_name(bh_clas) == target_class_name:
                cand_class = bh_clas
                break

        if cand_class is None:
            self._logger.warning(
                "Searched for an %s, %s, which has not been loaded",
                type(target_class).__name__,
                target_class_name,
            )
            raise ModuleNotFoundError(
                f"Cannot find {type(target_class).__name__} {target_class_name}"
            )

        if cand_class is not None and issubclass(cand_class, target_class):
            return cand_class

        raise AssertionError(
            f"Target class {target_class_name} "
            f"found, but was not a subclass of {type(target_class).__name__}"
        )

    # ------------
    # - IO CONFIGS

    def get_all_plugin_io_config_classes(self) -> Tuple[Type[IOConfig], ...]:
        """
        Returns the available IOConfig classes declared by all the plugins as a list.
        :return:
        """
        rtn_tuple: Tuple[Type[IOConfig], ...] = self._generic_get_all_plugin_classes(
            "get_io_config_classes", IOConfig
        )
        return rtn_tuple

    def get_classified_io_config_classes(self) -> Dict[str, Tuple[Type[IOConfig], ...]]:
        """
        Return the classified IOConfig classes.
        :return:
        """
        return self._generic_get_classified_plugin_classes("get_io_config_classes", IOConfig)

    def get_io_config(self, io_config_name: str) -> Type[IOConfig]:
        """
        Return the named IOConfig
        :param io_config_name: The name of the IOConfig to return
        :return:
        """
        return self._generic_get_plugin_class(
            getter_func="get_all_plugin_io_config_classes",
            target_class_name=io_config_name,
            target_class=IOConfig,
        )

    #
    # ------------
    # --------
    # - INPUTS

    def get_all_plugin_input_classes(self) -> Tuple[Type[Input], ...]:
        """
        Returns the available IOConfig classes declared by all the plugins as a list.
        :return:
        """
        return self._generic_get_all_plugin_classes("get_input_classes", Input)

    def get_classified_input_classes(self) -> Dict[str, Tuple[Type[Input], ...]]:
        """
        Return the classified Input classes.
        :return:
        """
        return self._generic_get_classified_plugin_classes("get_input_classes", Input)

    def get_input(self, input_name: str) -> Type[Input]:
        """
        Return the named Input
        :param input_name: The name of the IOConfig to return
        :return:
        """
        return self._generic_get_plugin_class(
            getter_func="get_input_classes", target_class_name=input_name, target_class=Input
        )

    # --------
    # ---------
    # - OUTPUTS

    def get_all_plugin_output_classes(self) -> Tuple[Type[Output], ...]:
        """
        Returns the available IOConfig classes declared by all the plugins as a list.
        :return:
        """
        return self._generic_get_all_plugin_classes("get_output_classes", Output)

    def get_classified_output_classes(self) -> Dict[str, Tuple[Type[Output], ...]]:
        """
        Return the classified Input classes.
        :return:
        """
        return self._generic_get_classified_plugin_classes("get_output_classes", Output)

    def get_output(self, output_name: str) -> Type[Output]:
        """
        Return the named Input
        :param input_name: The name of the IOConfig to return
        :return:
        """
        return self._generic_get_plugin_class(
            getter_func="get_all_plugin_output_classes",
            target_class_name=output_name,
            target_class=Output,
        )

    # ---------
    # ----------
    # - TRIGGERS

    def get_trigger(self, trigger_name: str) -> Type[Trigger]:
        """
        Return a specified condition by name.
        :param trigger_name:
        :return:
        """
        return self._generic_get_plugin_class(
            "get_all_plugin_trigger_classes",
            target_class_name=trigger_name,
            target_class=Trigger,
        )

    def get_all_plugin_trigger_classes(self) -> Tuple[Type[Trigger], ...]:
        """
        Returns the available Trigger classes declared by all the plugins as a list.
        :return:
        """
        return self._generic_get_all_plugin_classes("get_trigger_classes", Trigger)

    def get_classified_trigger_classes(self) -> Dict[str, Tuple[Type[Trigger], ...]]:
        """
        Return the classified Input classes.
        :return:
        """
        return self._generic_get_classified_plugin_classes("get_trigger_classes", Trigger)

    # ----------
    # ------------
    # - CONDITIONS

    def get_condition(self, condition_name: str) -> Type[Condition]:
        """
        Return a specified condition by name.
        :param condition_name:
        :return:
        """
        return self._generic_get_plugin_class(
            "get_all_plugin_condition_classes",
            target_class_name=condition_name,
            target_class=Condition,
        )

    def get_all_plugin_condition_classes(self) -> Tuple[Type[Condition], ...]:
        """
        Returns the available Condition classes declared by all the plugins as a list.
        :return:
        """
        return self._generic_get_all_plugin_classes("get_condition_classes", Condition)

    def get_classified_condition_classes(self) -> Dict[str, Tuple[Type[Condition], ...]]:
        """
        Return the classified Input classes.
        :return:
        """
        return self._generic_get_classified_plugin_classes("get_condition_classes", Condition)

    # ------------
    # --------
    # - ACTION

    def get_action(self, action_name: str) -> Type[Action]:
        """
        Return a specified action by name.
        :param action_name:
        :return:
        """
        return self._generic_get_plugin_class(
            "get_all_plugin_action_classes", action_name, Action
        )

    def get_all_plugin_action_classes(self) -> Tuple[Type[Action], ...]:
        """
        Returns the available Condition classes declared by all the plugins as a list.
        :return:
        """
        return self._generic_get_all_plugin_classes("get_action_classes", Action)

    def get_classified_action_classes(self) -> Dict[str, Tuple[Type[Action], ...]]:
        """
        Return the classified Input classes.
        :return:
        """
        return self._generic_get_classified_plugin_classes("get_action_classes", Action)

    # --------
    # -----------
    # - BEHAVIORS

    def get_behavior(self, behavior_name: str) -> Type[Behaviour]:
        """
        Return a specified behavior by name.
        :param behavior_name:
        :return:
        """
        return self._generic_get_plugin_class(
            "get_all_plugin_behavior_classes", behavior_name, Behaviour
        )

    def get_all_plugin_behavior_classes(self) -> Tuple[Type[Behaviour], ...]:
        """
        Returns the available Behavior classes declared by all the plugins as a tuple.
        :return:
        """
        return self._generic_get_all_plugin_classes("get_behavior_classes", Behaviour)

    def get_classified_behavior_classes(self) -> Dict[str, Tuple[Type[Behaviour], ...]]:
        """
        Return the classified Input classes.
        :return:
        """
        return self._generic_get_classified_plugin_classes("get_behavior_classes", Behaviour)

    # -----------
