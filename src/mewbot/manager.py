#!/usr/bin/env python3

"""Module which contains implementations of the optional manager class.
Mangers allow introspective actions - such as listing the bot status or all commands currently
active.
They also permit operations on the bot itself - such as enabling or disabling commands and viewing
history"""

from mewbot.bot import Bot, BotRunner

from typing import Dict, AnyStr


class Manager:

    _managed_bot: Bot
    _managed_bot_runner: BotRunner
    command_prefix: str

    # Commands for the manager - and are they enabled or not
    COMMANDS: Dict[AnyStr, bool] = {"status": True}

    def __init__(self, managed_bot: Bot, managed_bot_runner: BotRunner, command_prefix: str = "!"):

        self._managed_bot = managed_bot
        self._managed_bot_runner = managed_bot_runner

        self.command_prefix = command_prefix

    @property
    def bot(self):
        return self._managed_bot

    @bot.setter
    def bot(self, new_bot):
        raise AttributeError("Cannot change bot once manager has been initialized")

    async def status(self):
        """
        Generates a status string - where possible - for all the components.
        """











