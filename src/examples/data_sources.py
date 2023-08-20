# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Methods to support DSS examples.
"""

from __future__ import annotations

from typing import Any, AsyncIterable, Dict, Set, Type

import logging

from mewbot.api.v1 import Action, Condition, DataSource, pre_filter_non_matching_events
from mewbot.core import InputEvent, OutputEvent, OutputQueue
from mewbot.io.common import EventWithReplyMixIn, InputEventWithMessage


class RollDiceAction(Action):
    """
    Roll a dice by randomly selecting a value from a DataSource.
    """

    _logger: logging.Logger
    _queue: OutputQueue
    _message: str = ""
    _datasource: DataSource[Any]

    def __init__(self) -> None:
        """
        Accept a single data source - a list of values the dice roll could produce.

        :param datasource:
        """
        super().__init__()
        self._logger = logging.getLogger(__name__ + type(self).__name__)
        print(self._datasource)

    @property
    def die(self) -> DataSource[int]:
        return self._datasource

    @die.setter
    def die(self, die: DataSource[int]) -> None:
        self._datasource = die

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        Input Event types this Action will respond to.
        """
        return {EventWithReplyMixIn}

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        """
        Output Event types this method can produce.
        """
        return {OutputEvent}

    @property
    def message(self) -> str:
        """
        Response str to a message which passes selection.

        When a discord message in a monitored channel is detected which matches the command string,
        this message will be sent in response to it.
        :return:
        """
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        self._message = str(message)

    async def act(
        self, event: InputEvent, state: Dict[str, Any]
    ) -> AsyncIterable[OutputEvent]:
        """
        Construct a DiscordOutputEvent with the result of performing the calculation.
        """
        if not isinstance(event, EventWithReplyMixIn):
            return

        yield event.prepare_reply(
            f"A random value from a DataSource containing 1-6 was {self._datasource.random()}"
        )


class ExampleCondition(Condition):
    """
    A condition which passes on messages starting with "!" and filters others.
    """

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """
        The subtypes of InputEvent that this component accepts.

        This is used to save computational overhead by skipping events of the wrong type.
        Subclasses of the events specified here will also be processed.
        """
        return {InputEvent}

    @pre_filter_non_matching_events
    def allows(self, event: InputEventWithMessage) -> bool:
        """Whether the event is retained after passing through this filter."""
        return str(event.message).startswith("!")
