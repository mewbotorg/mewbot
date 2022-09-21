from __future__ import annotations

from typing import Generic, Optional, Type, TypeVar

import io
from abc import ABC

import yaml

from mewbot.bot import Bot
from mewbot.loader import load_component, configure_bot
from mewbot.core import Component
from mewbot.config import ConfigBlock


T_co = TypeVar("T_co", bound=Component, covariant=True)


class BaseTestClassWithConfig(ABC, Generic[T_co]):
    config_file: str
    implementation: Type[T_co]
    _config: Optional[ConfigBlock] = None
    _component: Optional[T_co] = None

    @property
    def config(self) -> ConfigBlock:
        """Returns the YAML-defined config the"""

        if not self._config:
            impl = self.implementation.__module__ + "." + self.implementation.__name__

            with open(self.config_file, "r", encoding="utf-8") as config:
                self._config = next(
                    document
                    for document in yaml.load_all(config, Loader=yaml.CSafeLoader)
                    if document["implementation"] == impl
                )

        return self._config

    @property
    def component(self) -> T_co:
        """Returns the component loaded from the config block"""

        if not self._component:
            component = load_component(self.config)
            assert isinstance(component, self.implementation), "Config loaded incorrect type"
            self._component = component

        return self._component


class TestTools:
    @staticmethod
    def get_trivial_post_bot() -> Bot:
        """

        :return:
        """
        test_post_bot_yaml = """
kind: IOConfig
implementation: mewbot.io.http.HTTPServlet
uuid: aaaaaaaa-aaaa-4aaa-0002-aaaaaaaaaa00
properties:
      host: localhost
      port: 12345

---

kind: Behaviour
implementation: mewbot.api.v1.Behaviour
uuid: aaaaaaaa-aaaa-4aaa-0002-aaaaaaaaaa01
properties:
  name: 'Echo Inputs'
triggers:
      - kind: Trigger
        implementation: mewbot.demo.AllEventTrigger
        uuid: aaaaaaaa-aaaa-4aaa-0002-aaaaaaaaaa02
        properties: { }
conditions: []
actions:
      - kind: Action
        implementation: mewbot.demo.PrintAction
        uuid: aaaaaaaa-aaaa-4aaa-0002-aaaaaaaaaa03
        properties: { }

            """
        yaml_stream = io.StringIO(test_post_bot_yaml)

        configured_bot = configure_bot(name="Please don't run this", stream=yaml_stream)

        return configured_bot

    @staticmethod
    def get_managed_discord_bot() -> Bot:
        """
        Get a bot setup - complete with a manager
        :return:
        """
        test_managed_bot_yaml = """
kind: IOConfig
implementation: mewbot.io.discord.DiscordIO
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa00
properties:
      token: "[token goes here]"

---

kind: Behaviour
implementation: mewbot.api.v1.Behaviour
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa01
properties:
  name: 'Echo Inputs'
triggers:
      - kind: Trigger
        implementation: examples.discord_bots.trivial_discord_bot.DiscordTextCommandTrigger
        uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa02
        properties:
          command: "!hello"
conditions: []
actions:
      - kind: Action
        implementation: examples.discord_bots.trivial_discord_bot.DiscordCommandTextResponse
        uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa03
        properties:
          message: "world"

---

kind: Manager
implementation: mewbot.manager.BasicManager
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa04
properties: {}

                    """
        yaml_stream = io.StringIO(test_managed_bot_yaml)

        configured_bot = configure_bot(name="Please don't run this", stream=yaml_stream)

        return configured_bot
