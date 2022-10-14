#!/usr/bin/env python3

"""
A series of conditions which are true (or not true) on various days of the week.
"""

# Todo: A general means, in the YAML, to negate conditions

from typing import Set, Type

from datetime import date

from mewbot.api.v1 import Condition, InputEvent


class MondayCondition(Condition):
    """
    Permits events if this is, in fact, Monday.
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        Hopefully this ... should work?
        :return:
        """
        return {
            InputEvent,
        }

    def allows(self, event: InputEvent) -> bool:
        """
        Permits events through if this is, in fact, Monday
        :param event:
        :return:
        """
        # Returns True if today is Monday (0 of 6)
        return date.today().weekday() == 0


class NotMondayCondition(Condition):
    """
    Permits events if this is not Monday.
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        Hopefully this ... should work?
        :return:
        """
        return {
            InputEvent,
        }

    def allows(self, event: InputEvent) -> bool:
        """
        Permits events through if this is, in fact, Monday
        :param event:
        :return:
        """
        # Returns True if today is Monday (0 of 6)
        return not date.today().weekday() == 0
