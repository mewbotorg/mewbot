# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Simple example elements which demonstrate some of the most basic mewbot objects.

This common elements are often used in various of the examples.
"""

from __future__ import annotations

from typing import Set, Type, Dict, Any

from mewbot.api.v1 import Condition, Trigger, Action, InputEvent, OutputEvent


class Foo(Condition):
    """
    Example, trivial, condition.
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """Foo consumes no Input Events."""
        return set()

    _channel: str

    @property
    def channel(self) -> str:
        """String representation of the channel this Condition acts on."""
        return self._channel

    @channel.setter
    def channel(self, val: str) -> None:
        self._channel = val

    def allows(self, event: InputEvent) -> bool:
        """Foo always matches any InputEvent passed to it."""
        return True

    def __str__(self) -> str:
        """Str rep of Foo - tells you what channel it's watching."""
        return f"Foo(channel={self.channel})"


class AllEventTrigger(Trigger):
    """
    Fires whenever there is an PostInputEvent.

    Will be used in the PrintBehavior.
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """This trigger consumes all Input Events."""
        return {InputEvent}

    def matches(self, event: InputEvent) -> bool:
        """This trigger will always match - as this method always returns True."""
        return True


class PrintAction(Action):
    """
    Print every InputEvent.
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """This action triggers on all InputEvents."""
        return {InputEvent}

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        """This action cannot produce any OutputEvents."""
        return set()

    async def act(self, event: InputEvent, state: Dict[str, Any]) -> None:
        """
        Just print every event which comes through - which should be all of them.

        This action should print any event the triggers match - used for debugging.
        :param event:
        :param state:
        :return:
        """
        print("Processed event", event)
