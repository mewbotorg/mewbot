#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

# pylint: disable=duplicate-code
# this is an example - duplication for emphasis is desirable

"""
The actions for this discord dice roller bot call d20 to actually produce the output.

It parses the incoming string, uses it in d20, and produces a result.
"""


from __future__ import annotations

from typing import Any, Dict, Set, Type, AsyncIterable

import logging

import d20  # type: ignore

from mewbot.api.v1 import Action
from mewbot.core import InputEvent, OutputEvent, OutputQueue
from mewbot.io.discord import DiscordMessageCreationEvent, DiscordOutputEvent


class DiscordRollTextResponse(Action):
    """
    Parse the payload, roll the dice and return.
    """

    _logger: logging.Logger
    _queue: OutputQueue

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__ + type(self).__name__)

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        This action only responds to DiscordMessageCreationEvents.

        :return:
        """
        return {DiscordMessageCreationEvent}

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        """
        Produces DiscordOutputEvents - which should be replies to the original message.

        :return:
        """
        return {DiscordOutputEvent}

    async def act(
        self, event: InputEvent, state: Dict[str, Any]
    ) -> AsyncIterable[OutputEvent | None]:
        """
        Construct a DiscordOutputEvent with the result of rolling the dice.
        """
        if not isinstance(event, DiscordMessageCreationEvent):
            self._logger.warning("Received wrong event type %s", type(event))
            return

        msg_text = str(event.message.content)

        # A way to directly get at the code of this while running would be good
        if not msg_text.startswith("!roll"):
            self._logger.warning("Received a message with bad content %s", msg_text)
            return

        msg_payload = msg_text[5:].strip()

        self._logger.info('Calling d20.roll with payload "%s"', msg_payload)
        try:
            payload_result = d20.roll(msg_payload)
        except d20.errors.RollSyntaxError as exp:
            self._logger.warning(
                "d20 got an input it could not parse - %s - %s", msg_payload, exp
            )
            return

        test_event = DiscordOutputEvent(
            text=payload_result, message=event.message, use_message_channel=True
        )

        yield test_event
