# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Primitive example elements which demonstrate some of the most basic mewbot objects.
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
        return set()

    _channel: str

    @property
    def channel(self) -> str:
        """
        string representation of the channel this Condition acts on.
        :return:
        """
        return self._channel

    @channel.setter
    def channel(self, val: str) -> None:
        self._channel = val

    def allows(self, event: InputEvent) -> bool:
        return True

    def __str__(self) -> str:
        return f"Foo(channel={self.channel})"


class AllEventTrigger(Trigger):
    """
    Nothing fancy - just fires whenever there is an PostInputEvent.
    Will be used in the PrintBehavior.
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        return {InputEvent}

    def matches(self, event: InputEvent) -> bool:
        return True


class PrintAction(Action):
    """
    Print every InputEvent.
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        return {InputEvent}

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        return set()

    async def act(self, event: InputEvent, state: Dict[str, Any]) -> None:
        print("Processed event", event)
