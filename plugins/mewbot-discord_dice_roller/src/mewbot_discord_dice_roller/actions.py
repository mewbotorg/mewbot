#!/usr/bin/env python3
# pylint: disable=duplicate-code
# this is an example - duplication for emphasis is desirable

from __future__ import annotations

from typing import Any, Dict, Set, Type

import logging

import d20  # type: ignore

from mewbot.api.v1 import Action
from mewbot.core import InputEvent, OutputEvent, OutputQueue
from mewbot.io.discord import DiscordMessageCreationEvent, DiscordOutputEvent


class DiscordRollTextResponse(Action):
    """
    Parse the payload, roll the dice and return
    """

    _logger: logging.Logger
    _queue: OutputQueue

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__ + type(self).__name__)

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        return {DiscordMessageCreationEvent}

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        return {DiscordOutputEvent}

    async def act(self, event: InputEvent, state: Dict[str, Any]) -> None:
        """
        Construct a DiscordOutputEvent with the result of performing the calculation.
        """
        if not isinstance(event, DiscordMessageCreationEvent):
            self._logger.warning("Received wrong event type %s", type(event))
            return

        msg_text = str(event.message.content)

        # A way to directly get at the code of this while running would be good
        if not msg_text.startswith("!roll"):
            self._logger.warning("Received a message with bad content %s", msg_text)
            return

        msg_payload = msg_text[5:]
        payload_result = d20.roll(msg_payload)

        test_event = DiscordOutputEvent(
            text=payload_result, message=event.message, use_message_channel=True
        )

        await self.send(test_event)
