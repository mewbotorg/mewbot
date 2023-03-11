# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Provides tests for mewbot core operations.
In particular, that the interfaces for the various components match expectations.
"""


from __future__ import annotations

import pytest

from mewbot.core import (
    ComponentKind,
    BehaviourInterface,
    TriggerInterface,
    ConditionInterface,
    ActionInterface,
    IOConfigInterface,
)


# pragma pylint: disable=R0903
#  Disable "too few public methods" for test cases - most test files will be classes used for
#  grouping and then individual tests alongside these


class TestComponent:
    """
    Test a set of what interface passing succeeds and fails.
    """

    @staticmethod
    def test_componentkind_interface_map_behaviour() -> None:
        """
        The interface method returns the interface supported by that Component.

        In this case, a Behavior type object should present a BehaviorInterface
        :return:
        """
        assert (
            ComponentKind.interface(ComponentKind(ComponentKind.Behaviour))
            == BehaviourInterface
        )

    @staticmethod
    def test_componentkind_interface_map_trigger() -> None:
        """
        The interface method returns the interface supported by that Component.

        In this case, a Trigger type object should present a TriggerInterface
        :return:
        """
        assert (
            ComponentKind.interface(ComponentKind(ComponentKind.Trigger)) == TriggerInterface
        )

    @staticmethod
    def test_componentkind_interface_map_condition() -> None:
        """
        The interface method returns the interface supported by that Component.

        In this case, a Condition type object should present a ConditionInterface
        :return:
        """
        assert (
            ComponentKind.interface(ComponentKind(ComponentKind.Condition))
            == ConditionInterface
        )

    @staticmethod
    def test_componentkind_interface_map_action() -> None:
        """
        The interface method returns the interface supported by that Component.

        In this case, a Action type object should present a ActionInterface
        :return:
        """
        assert ComponentKind.interface(ComponentKind(ComponentKind.Action)) == ActionInterface

    @staticmethod
    def test_componentkind_interface_map_ioconfig() -> None:
        """
        The interface method returns the interface supported by that Component.

        In this case, a IOConfig type object should present a IOConfigInterface
        :return:
        """
        assert (
            ComponentKind.interface(ComponentKind(ComponentKind.IOConfig))
            == IOConfigInterface
        )

    @staticmethod
    def test_componentkind_interface_map_datasource() -> None:
        """
        The interface method returns the interface supported by that Component.

        However, DataSource interfaces have not, yet, been defined.
        As such, a lookup on them should fail.
        :return:
        """
        with pytest.raises(ValueError):  # @UndefinedVariable
            _ = ComponentKind.interface(ComponentKind(ComponentKind.DataSource))

    @staticmethod
    def test_componentkind_interface_map_template() -> None:
        """
        The interface method returns the interface supported by that Component.

        However, Template interfaces have not, yet, been defined.
        As such, a lookup on them should fail.
        :return:
        """
        with pytest.raises(ValueError):  # @UndefinedVariable
            _ = ComponentKind.interface(ComponentKind(ComponentKind.Template))

    @staticmethod
    def test_componentkind_values_list() -> None:
        """
        Lists the valid ComponentKinds - in particular, checks "Behavior" is in this list.

        :return:
        """
        values = ComponentKind.values()
        assert isinstance(values, list)
        assert "Behaviour" in values
