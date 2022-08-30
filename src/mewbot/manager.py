#!/usr/bin/env python3

"""Module which contains implementations of the optional manager class.
Mangers allow introspective actions - such as listing the bot status or all commands currently
active.
They also permit operations on the bot itself - such as enabling or disabling commands and viewing
history"""

import logging
import pprint

from mewbot.bot import Bot, BotRunner

from typing import Dict, AnyStr


class Manager:

    _managed_bot: Bot
    _managed_bot_runner: BotRunner
    command_prefix: str
    _logger: logging.Logger

    # Commands for the manager - and are they enabled or not
    COMMANDS: Dict[AnyStr, bool] = {"status": True}

    def __init__(self, managed_bot: Bot, managed_bot_runner: BotRunner, command_prefix: str = "!") -> None:

        self._managed_bot = managed_bot
        self._managed_bot_runner = managed_bot_runner

        self.command_prefix = command_prefix

        self._logger = logging.getLogger(__name__ + "Manager")

    @property
    def bot(self) -> Bot:
        return self._managed_bot

    @bot.setter
    def bot(self, new_bot) -> None:
        raise AttributeError("Cannot change bot once manager has been initialized")

    async def status(self) -> Dict[AnyStr, Dict[AnyStr, AnyStr]]:
        """
        Generates a status string - where possible - for all the components.
        """
        # Stored like this so custom renders can be applied - later
        status: Dict[AnyStr, Dict[AnyStr, AnyStr]] = dict()

        # IOConfigs
        status["io_configs"] = dict()
        for io_conf in self._managed_bot.get_io_configs():
            try:
                status["io_configs"][io_conf.__name__] = await io_conf.status()
            except AttributeError:
                status["io_configs"][io_conf.__name__] = "No status could be generated"

        # Behaviors
        status["behaviors"] = dict()
        for behavior in self._managed_bot.get_behaviours():
            try:
                status["behaviors"][behavior.__name__] = await behavior.status()
            except AttributeError:
                status["behaviors"][behavior.__name__] = "No status could be generated"

        self._logger.info(self.render_status(status))
        return status

    @staticmethod
    def render_status(status: Dict[AnyStr, Dict[AnyStr, AnyStr]]) -> str:
        return pprint.pformat(status)



