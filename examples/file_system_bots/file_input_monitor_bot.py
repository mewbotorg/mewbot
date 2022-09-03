#!/usr/bin/env python3
# pylint: disable=duplicate-code
# this is an example - duplication for emphasis is desirable

from __future__ import annotations

from typing import Any, Dict, Set, Type

import logging

from mewbot.api.v1 import Trigger, Action
from mewbot.core import InputEvent, OutputEvent, OutputQueue
from mewbot.io.file_system import FileMonitorInputEvent


class FileSystemAllCommandTrigger(Trigger):
    """
    Nothing fancy - just fires whenever there is a file related FSInputEvent
    """

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        return {FileMonitorInputEvent}

    def matches(self, event: InputEvent) -> bool:
        if not isinstance(event, FileMonitorInputEvent):
            return False

        return True


class FileSystemInputPrintResponse(Action):
    """
    Print every FileSystem File related InputEvent.
    """

    _logger: logging.Logger
    _queue: OutputQueue

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__ + type(self).__name__)

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        return {FileMonitorInputEvent}

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        return set()

    async def act(self, event: InputEvent, state: Dict[str, Any]) -> None:
        """
        Construct a DiscordOutputEvent with the result of performing the calculation.
        """
        if not isinstance(event, FileMonitorInputEvent):
            self._logger.warning("Received wrong event type %s", type(event))
            return

        print(event)
