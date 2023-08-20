# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests the modules which load mewbot components from yaml configurations.

Also serves an example of how to construct these sort of tests.
"""

from __future__ import annotations

from typing import Type

import copy
import io
import textwrap
from io import StringIO

import pytest
import yaml

from mewbot.api.v1 import Behaviour, IOConfig
from mewbot.bot import Bot
from mewbot.core import ConfigBlock
from mewbot.io.http import HTTPServlet
from mewbot.loader import configure_bot, load_behaviour, load_component
from mewbot.test import BaseTestClassWithConfig

CONFIG_YAML = "examples/trivial_http_post.yaml"


class TestLoader:
    """
    Tests the load_component method fails when passed bad ConfigBlocks.
    """

    @staticmethod
    def test_empty_config() -> None:
        """
        Attempt to load a component from an empty config block.
        """
        # Build a bad config and give it to the bot
        this_config = ConfigBlock()  # type: ignore
        with pytest.raises(ValueError):
            _ = load_component(this_config)

    @staticmethod
    def test_bad_config() -> None:
        """
        Attempt to load a component from a config block with an invalid kind ("NULL").
        """
        # Build a bad config and give it to the bot
        this_config = ConfigBlock()  # type: ignore
        this_config["kind"] = "NULL"
        with pytest.raises(ValueError):  # @UndefinedVariable
            _ = load_component(this_config)


class TestLoaderConfigureBot:
    """
    Tests basic loading a bot from a valid yaml configuration file.
    """

    @staticmethod
    def test_config_type() -> None:
        """
        Read the current config yaml under test (currently "trivial_http_post.yaml").

        Checks that at least one component loaded from this yaml is a v1 Behavior.
        """
        with open(CONFIG_YAML, "r", encoding="utf-8") as config_file:
            config = list(yaml.load_all(config_file, Loader=yaml.CSafeLoader))

        assert len(config) > 1
        assert any(
            obj for obj in config if obj["implementation"] == "mewbot.api.v1.Behaviour"
        )

    @staticmethod
    def test_working() -> None:
        """
        Read the current config yaml under test (currently "trivial_http_post.yaml").

        Checks that this yaml represents a valid bot.
        (i.e. that passing the yaml file handle to configure_bot yields a valid bot).
        """
        with open(CONFIG_YAML, "r", encoding="utf-8") as config_file:
            bot = configure_bot("bot", config_file)

        assert isinstance(bot, Bot)


# Tester for mewbot.loader.load_component
class TestLoaderHttpsPost(BaseTestClassWithConfig[HTTPServlet]):
    """
    Loads the example yaml file "examples/trivial_http_post.yaml".

    This should contain an HTTP post IOConfig (subclass of HTTPServlet).
    This component will be isolated for testing as self.component after load.
    """

    config_file: str = CONFIG_YAML
    implementation: Type[HTTPServlet] = HTTPServlet

    # Test this working
    def test_working(self) -> None:
        """
        Tests that load_component successfully loads an IOConfig from the YAML.

        :param self.config:.
        self.config should be an IOConfig of type specified in this class by setting the
        implementation class variable.
        """
        component = load_component(self.config)
        assert isinstance(component, IOConfig)

    # Test that the loading is accurate
    def test_loading_component_type(self) -> None:
        """
        Tests that the :param self.component: class property is of the expected type.

        In this case, an HTTPServlet.
        """
        assert isinstance(self.component, HTTPServlet)

    def test_loading_component_config(self) -> None:
        """
        Test loading a component has correct set properties.

        Check that the :param self.component.host: and :param self.componentport: values are as set
        in the example yaml file.
        :param self.component: has been loaded from the test yaml, (currently
                               "trivial_http_post.yaml").

        :return:
        """
        assert self.component.host == "localhost"
        assert self.component.port == 12345

    def test_loading_component_values(self) -> None:
        """
        Test loading a component has correct set properties.

        :param self.component: has been loaded from the test yaml, (currently
        "trivial_http_post.yaml").
        Check that the internal variables which underlie :param self.component.host: and
        :param self.componentport: values are as set in the example yaml file.

        :return None:
        """
        # Protected access overridden here to inspect variables ONLY
        assert self.component._host == "localhost"  # pylint: disable="protected-access"
        assert self.component._port == 12345  # pylint: disable="protected-access"

    # Tests that expose errors
    def test_erroring_kind(self) -> None:
        """
        Test loading with an invalid `kind` value.

        Copy :param self.config:
        Change the "kind" variable of this config to an invalid entry - "NULL".
        Then attempt to load_component from this - now invalid - config.
        This should always fail with ValueError.

        :return:
        """
        # Change the kind of this config, to break it
        this_config = copy.deepcopy(self.config)
        this_config["kind"] = "NULL"
        with pytest.raises(ValueError):  # @UndefinedVariable
            _ = load_component(this_config)


class TestLoaderBehaviourHttpPost(BaseTestClassWithConfig[Behaviour]):
    """
    Tests loading a Behaviour from the HttpPost example bot.
    """

    config_file: str = CONFIG_YAML
    implementation: Type[Behaviour] = Behaviour

    # Test this working
    def test_config_type(self) -> None:
        """
        Example yaml file presents an IOConfig and a Behavior config.

        The Behavior config should have been isolated in :param self.config:.
        Testing that this has occurred and the yaml block contains the expected entries.

        :return:
        """
        assert "triggers" in self.config
        assert "conditions" in self.config
        assert "actions" in self.config

    # Test this working
    def test_working(self) -> None:
        """
        Check that loading the config returns a Behaviour.

        Attempt to load the config in :param self.config: - which should correspond to an instance
        of the class set as :param self.implementation:.

        :return:
        """
        component = load_behaviour(self.config)  # type: ignore
        assert isinstance(component, Behaviour)

    @staticmethod
    def test_resetting_uuid() -> None:
        """Test attempting to change UUID of a component."""
        error = "Can not set the ID of a component outside of creation"
        # pylint: disable=unexpected-keyword-arg
        behaviour = Behaviour(name="Test")  # type: ignore
        with pytest.raises(AttributeError, match=error):
            behaviour.uuid = "0"

    @staticmethod
    def test_load_incomplete_document() -> None:
        """
        Tests loading a document which is incomplete - lacking a uuid.
        """

        test_yaml_doc = textwrap.dedent(
            """
kind: IOConfig
implementation: mewbot.io.discord.DiscordIO
properties:
  token: "[token-goes-here]"

---
        """
        )

        try:
            configure_bot(name="This should fail", stream=io.StringIO(test_yaml_doc))
        except ValueError:
            pass

    @staticmethod
    def test_load_datasource_from_yaml() -> None:
        """
        Tests loading a document which contains a single DataSource.
        """

        test_yaml_doc = textwrap.dedent(
            """
kind: DataSource
name: vals_for_d6
implementation: mewbot.data.json_data.JsonStringDataSourceListValues
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa00
datatype: int
properties:
  json_string: '[1, 2, 3, 4, 5, 6]'

        """
        )

        configure_bot(name="This should pass", stream=io.StringIO(test_yaml_doc))

    @staticmethod
    def test_load_component_bad_implementation() -> None:
        """
        Tests loading a document which is incomplete - lacking a uuid.
        """

        test_yaml_doc = textwrap.dedent(
            """
kind: IOConfig
implementation: io.StringIO
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa00
properties:
  token: "[token-goes-here]"

---
        """
        )

        for document in yaml.load_all(StringIO(test_yaml_doc), Loader=yaml.CSafeLoader):
            if document is None:
                continue

            try:
                load_component(config=document, data_sources=None)
            except TypeError:
                pass

    @staticmethod
    def test_load_bot_with_condition() -> None:
        """
        Tests loading a document which is incomplete - lacking a uuid.
        """

        test_bot_yaml = """

kind: DataSource
name: vals_for_d6
implementation: mewbot.data.json_data.JsonStringDataSourceListValues
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa00
datatype: int
properties:
  json_string: '[1, 2, 3, 4, 5, 6]'

---

kind: IOConfig
implementation: mewbot.io.discord.DiscordIO
uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa00
properties:
  token: "[token-goes-here]"

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
      command: "!dice"
conditions:
  - kind: Condition
    uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa03
    implementation: examples.data_sources.ExampleCondition
    properties: {}
actions:
  - kind: Action
    implementation: examples.data_sources.RollDiceAction
    uuid: aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa04
    properties:
      datasource: vals_for_d6


"""

        configure_bot(name="Bot with a condition", stream=io.StringIO(test_bot_yaml))
