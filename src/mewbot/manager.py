#!/usr/bin/env python3

"""Module which contains implementations of the optional manager class.
Mangers allow introspective actions - such as listing the bot status or all commands currently
active.
They also permit operations on the bot itself - such as enabling or disabling commands and viewing
history"""

import dataclasses
import logging
import pprint

from typing import Dict, AnyStr

from mewbot.api.v1 import InputEvent
from mewbot.bot import Bot, BotRunner


@dataclasses.dataclass
class ManagerInputEvent(InputEvent):

    trigger_input_event: InputEvent


class Manager:

    _managed_bot: Bot
    _managed_bot_runner: BotRunner
    command_prefix: str
    _logger: logging.Logger

    # Commands for the manager - and are they enabled or not
    COMMANDS: Dict[str, bool] = {"status": True}

    def __init__(
        self, managed_bot: Bot, managed_bot_runner: BotRunner, command_prefix: str = "!"
    ) -> None:

        self._managed_bot = managed_bot
        self._managed_bot_runner = managed_bot_runner

        self.command_prefix = command_prefix

        self._logger = logging.getLogger(__name__ + "Manager")

    @property
    def bot(self) -> Bot:
        return self._managed_bot

    @bot.setter
    def bot(self, new_bot: Bot) -> None:
        raise AttributeError("Cannot change bot once manager has been initialized")

    async def status(self) -> Dict[str, Dict[str, str]]:
        """
        Generates a status string - where possible - for all the components.
        """
        # Stored like this so custom renders can be applied - later
        status: Dict[str, Dict[str, str]] = {}

        # IOConfigs
        status["io_configs"] = {}
        for io_conf in self._managed_bot.get_io_configs():
            status["io_configs"][str(io_conf)] = await io_conf.status()

        # Behaviors
        status["behaviors"] = {}
        for behavior in self._managed_bot.get_behaviours():
            status["behaviors"][str(behavior)] = await behavior.status()

        self._logger.info(self.render_status(status))
        return status

    @staticmethod
    def render_status(status: Dict[AnyStr, Dict[AnyStr, AnyStr]]) -> str:
        return pprint.pformat(status)
