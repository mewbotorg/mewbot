from __future__ import annotations

from typing import Type

import copy
import pytest
import yaml

from tests.common import BaseTestClassWithConfig

from mewbot.loader import configure_bot, load_behaviour, load_component

from mewbot.bot import Bot
from mewbot.config import ConfigBlock
from mewbot.api.v1 import IOConfig, Behaviour
from mewbot_reddit.io_configs.reddit_password_io import RedditPasswordIO

from .common import BasePathTools


CONFIG_YAML = "examples/trivial_reddit_bot.yaml"
CONFIG_YAML_NAME = "trivial_reddit_bot.yaml"


class TestLoader:
    @staticmethod
    def test_empty_config() -> None:
        # Build a bad config and give it to the bot
        this_config = ConfigBlock()  # type: ignore
        with pytest.raises(ValueError):  # @UndefinedVariable
            _ = load_component(this_config)

    @staticmethod
    def test_bad_config() -> None:
        # Build a bad config and give it to the bot
        this_config = ConfigBlock()  # type: ignore
        this_config["kind"] = "NULL"
        with pytest.raises(ValueError):  # @UndefinedVariable
            _ = load_component(this_config)


class TestLoaderConfigureBot(BasePathTools):

    def test_config_type(self) -> None:

        config_path = self.get_example_path(CONFIG_YAML_NAME)

        with open(config_path, "r", encoding="utf-8") as config_file:
            config = list(yaml.load_all(config_file, Loader=yaml.CSafeLoader))

        assert len(config) > 1
        assert any(
            obj for obj in config if obj["implementation"] == "mewbot.api.v1.Behaviour"
        )

    def test_working(self) -> None:

        config_path = self.get_example_path(CONFIG_YAML_NAME)

        with open(config_path, "r", encoding="utf-8") as config_file:
            bot = configure_bot("bot", config_file)

        assert isinstance(bot, Bot)


# # Tester for mewbot.loader.load_component
# class TestLoaderRSSInput(BaseTestClassWithConfig[RedditPasswordIO]):
#     config_file: str = CONFIG_YAML
#     implementation: Type[RedditPasswordIO] = RedditPasswordIO
#
#     # Test this working
#     def test_working(self) -> None:
#         component = load_component(self.config)
#         assert isinstance(component, IOConfig)
#
#     # Test that the loading is accurate
#     def test_loading_component_type(self) -> None:
#         assert isinstance(self.component, RedditPasswordIO)
#
#     def test_loading_component_config(self) -> None:
#         assert self.component.host == "localhost"
#         assert self.component.port == 12345
#
#     def test_loading_component_values(self) -> None:
#         # Protected access overridden here to inspect variables ONLY
#         assert self.component._host == "localhost"  # pylint: disable="protected-access"
#         assert self.component._port == 12345  # pylint: disable="protected-access"
#
#     # Tests that expose errors
#     def test_erroring_kind(self) -> None:
#         # Change the kind of this config, to break it
#         this_config = copy.deepcopy(self.config)
#         this_config["kind"] = "NULL"
#         with pytest.raises(ValueError):  # @UndefinedVariable
#             _ = load_component(this_config)
#
#
# # Test for mewbot.loader.load_behaviour
# class TestLoaderBehaviourHttpPost(BaseTestClassWithConfig[Behaviour]):
#     config_file: str = CONFIG_YAML
#     implementation: Type[Behaviour] = Behaviour
#
#     # Test this working
#     def test_config_type(self) -> None:
#         assert "triggers" in self.config
#         assert "conditions" in self.config
#         assert "actions" in self.config
#
#     # Test this working
#     def test_working(self) -> None:
#         component = load_behaviour(self.config)  # type: ignore
#         assert isinstance(component, Behaviour)
