#!/usr/bin/env python3

"""Module which contains implementations of the optional manager class.
Mangers allow introspective actions - such as listing the bot status or all commands currently
active.
They also permit operations on the bot itself - such as enabling or disabling commands and viewing
history"""

from typing import Dict, Set, Union, List

import logging
import yaml

from mewbot.api.v1 import Manager
from mewbot.bot import Bot, BotRunner
from mewbot.core import ManagerInputEvent, ManagerInfoInputEvent


class BasicManager(Manager):

    _managed_bot: Bot
    _managed_bot_runner: BotRunner
    command_prefix: str
    _logger: logging.Logger

    # Commands for the manager - and are they enabled or not
    COMMANDS: Dict[str, bool] = {"status": True}

    def __init__(self, command_prefix: str = "!") -> None:

        self.command_prefix = command_prefix

        self._logger = logging.getLogger(__name__ + "Manager")

    @property
    def bot(self) -> Bot:
        return self._managed_bot

    @bot.setter
    def bot(self, new_bot: Bot) -> None:
        raise AttributeError("Cannot change bot once manager has been initialized")

    def get_trigger_data(self) -> Dict[str, Set[str]]:
        return {
            "simple_strs": {
                self.command_prefix + "status",
            }
        }

    async def run(self) -> None:
        """
        Run the manager.
        The manager is intended to run parallel to the bot itseld, gathering information and
        providing a control interface to it.
        """
        self._logger.info("Manager %s starting", self)

        while self.manager_input_queue:

            manager_input_event: ManagerInputEvent = await self.manager_input_queue.get()

            if isinstance(manager_input_event, ManagerInfoInputEvent):
                cmd_text = self.strip_command_prefix(manager_input_event.info_type)
            else:
                continue

            if cmd_text == "status":
                status_dict = await self.status()
                status_str = self.render_status(status_dict)
                print(status_str)

    def strip_command_prefix(self, cmd_text: str) -> str:
        """
        Strip the manager command prefix - intended to bring the command into standard form.
        """
        # Originally
        # return cmd_text[len(self.command_prefix):]
        # but black on windows keeps adding whitespace before the : - for some reason
        # which annoys the linters
        cmd_prefix_length = len(self.command_prefix)
        return cmd_text[cmd_prefix_length:]

    async def status(self) -> Dict[str, Dict[str, Union[str, Dict[str, List[str]]]]]:
        """
        Generates a status string - where possible - for all the components.
        """
        # Stored like this so custom renders can be applied - later
        status: Dict[str, Dict[str, Union[str, Dict[str, List[str]]]]] = {}

        # IOConfigs
        status["io_configs"] = {}
        for io_conf in self._managed_bot.get_io_configs():
            # Return is a dict, keyed with the input/output str and valued with its status
            status["io_configs"][str(io_conf)] = await io_conf.status()

        # Behaviors
        status["behaviors"] = {}
        for behavior in self._managed_bot.get_behaviours():
            # Return is a dict, keyed with the behavior str and valued with its status
            status["behaviors"][str(behavior)] = await behavior.status()

        # Datastores
        # To be added

        return status

    async def help(self) -> Dict[str, Dict[str, str]]:
        return {}

    @staticmethod
    def render_status(status: Dict[str, Dict[str, Union[str, Dict[str, List[str]]]]]) -> str:
        return str(yaml.dump(status, default_flow_style=False))
