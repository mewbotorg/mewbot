#!/usr/bin/env python3

from __future__ import annotations

from typing import Any, Dict, Set, Type

import logging

from mewbot.api.v1 import Trigger, Action
from mewbot.core import InputEvent, OutputEvent, OutputQueue
from mewbot.io.discord import DiscordInputEvent
from mewbot.io.desktop_notification import DesktopNotificationOutputEvent


class DiscordTextCommandTrigger(Trigger):
    """
    Nothing fancy - just fires whenever there is a DiscordInputEvent
    """

    _command: str = ""

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        return {DiscordInputEvent}

    @property
    def command(self) -> str:
        return self._command

    @command.setter
    def command(self, command: str) -> None:
        self._command = str(command)

    def matches(self, event: InputEvent) -> bool:
        if not isinstance(event, DiscordInputEvent):
            return False

        return event.text == self._command


class DiscordMessageToNotificationAction(Action):
    """
    Print every InputEvent.
    """

    _logger: logging.Logger
    _queue: OutputQueue
    _message: str = ""

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__ + type(self).__name__)

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        return {DiscordInputEvent}

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        return {DesktopNotificationOutputEvent}

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        self._message = str(message)

    async def act(self, event: InputEvent, state: Dict[str, Any]) -> None:
        """
        Construct a DiscordOutputEvent with the result of performing the calculation.
        """
        if not isinstance(event, DiscordInputEvent):
            self._logger.warning("Received wrong event type %s", type(event))
            return

        test_event = DesktopNotificationOutputEvent(
            title="Someone said hello!",
            text=self._message,
        )
        self._logger.info("Triggering DesktopNotification %s", test_event)

        await self.send(test_event)
