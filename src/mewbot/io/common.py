# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Simple example elements which demonstrate some of the most basic mewbot objects.

This common elements are often used in various of the examples.
"""

from __future__ import annotations

import abc

from collections.abc import AsyncIterable
from string import Template
from typing import Any

from mewbot.api.v1 import Trigger, Action, InputEvent, OutputEvent


class AllEventTrigger(Trigger):
    """
    Fires whenever there is an PostInputEvent.

    Will be used in the PrintBehavior.
    """

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
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
    def consumes_inputs() -> set[type[InputEvent]]:
        """This action triggers on all InputEvents."""
        return {InputEvent}

    @staticmethod
    def produces_outputs() -> set[type[OutputEvent]]:
        """This action cannot produce any OutputEvents."""
        return set()

    async def act(self, event: InputEvent, state: dict[str, Any]) -> AsyncIterable[None]:
        """
        Just print every event which comes through - which should be all of them.

        This action should print any event the triggers match - used for debugging.
        :param event:
        :param state:
        :return:
        """
        print("Processed event", event)
        yield None
