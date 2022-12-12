# Loads a file in, sees if it works

from __future__ import annotations

from typing import Type, Optional, Dict, Set

import pytest

from tests.common import BaseTestClassWithConfig

from mewbot.io.discord import DiscordIO, DiscordInput, DiscordOutput
from mewbot.core import (
    InputEvent,
    OutputEvent,
    InputQueue,
    ManagerInputQueue,
    ManagerOutputQueue,
)
from mewbot.api.v1 import IOConfig

# pylint: disable=R0903
#  Disable "too few public methods" for test cases - most test files will be classes used for
#  grouping and then individual tests alongside these


class TestIoDiscordFromYAML(BaseTestClassWithConfig[DiscordIO]):
    config_file: str = "examples/discord_bots/trivial_discord_bot.yaml"
    implementation: Type[DiscordIO] = DiscordIO

    def test_check_class(self) -> None:
        assert isinstance(self.component, DiscordIO)
        assert isinstance(self.component, IOConfig)

    @pytest.mark.asyncio
    async def test_io_config_set_io_config_uuids(self) -> None:
        """
        Should set the io_config_uuid for all the input methods.
        :return:
        """
        theo_io_config_uuid = "aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa00"

        assert self.component.uuid == theo_io_config_uuid
        assert self.component.get_uuid() == theo_io_config_uuid

        self.component.set_io_config_uuids()

        discord_input = self.component.get_inputs()[0]
        assert discord_input.get_io_config_uuid() == theo_io_config_uuid

        discord_output = self.component.get_outputs()[0]
        assert discord_output.get_io_config_uuid() == theo_io_config_uuid


class TestDiscordInput:
    @pytest.mark.asyncio  # Need a running event loop to avoid warnings
    async def test_discord_input_init_and_properties(self) -> None:
        """
        Directly tests the Input part of discord IO.
        :return:
        """
        test_discord_input = DiscordInput(token="[Not set for this test]")
        # No queue should be bound
        assert test_discord_input.queue is None

        # uuid should be set by this startup process
        assert isinstance(test_discord_input.uuid, str)
        assert test_discord_input.get_uuid() == test_discord_input.uuid

        try:
            test_discord_input.uuid = "this is a very bad uuid"
        except AttributeError:
            pass

        assert isinstance(test_discord_input.get_io_config_uuid(), str)

        # Attempt to set the io_config_uuid
        uuid_test_str = "this is a bad uuid"
        test_discord_input.set_io_config_uuid(new_uuid=uuid_test_str)
        assert test_discord_input.get_io_config_uuid() == uuid_test_str

    @pytest.mark.asyncio
    async def test_discord_input_bind(self) -> None:
        """
        Directly tests the Input part of discord IO.
        Test basic bindings of appropriate queues.
        :return:
        """
        test_discord_input = DiscordInput(token="[Not set for this test]")
        assert test_discord_input.queue is None

        test_input_queue = InputQueue()
        test_manager_data: Optional[Dict[str, Set[str]]] = {}
        test_manager_input = ManagerInputQueue()
        test_manager_output = ManagerOutputQueue()

        test_discord_input.bind(
            queue=test_input_queue,
            manager_trigger_data=test_manager_data,
            manager_input_queue=test_manager_input,
            manager_output_queue=test_manager_output,
        )

    @pytest.mark.asyncio
    async def test_discord_status(self) -> None:
        """
        Directly tests the Input part of discord IO.
        Calls status - checks it returns a string,
        :return:
        """
        test_discord_input = DiscordInput(token="[Not set for this test]")
        assert test_discord_input.queue is None

        status_str: str = await test_discord_input.status()
        assert isinstance(status_str, str)

    @staticmethod
    def test_discord_input_produced_inputs() -> None:
        """
        Tests that the produced_inputs method produces a set of InputEvent derived classes.
        :return:
        """
        test_discord_input = DiscordInput(token="[Not set for this test]")
        inputs = test_discord_input.produces_inputs()

        assert isinstance(inputs, set)

        for discord_input in inputs:
            assert issubclass(discord_input, InputEvent)


class TestDiscordOutput:
    @pytest.mark.asyncio  # Need a running event loop to avoid warnings
    async def test_discord_output_init_and_properties(self) -> None:
        """
        Directly tests the Input part of discord IO.
        :return:
        """
        test_discord_output = DiscordOutput()

        try:
            test_discord_output.uuid = "this is a very bad uuid"
        except AttributeError:
            pass

        assert isinstance(test_discord_output.get_io_config_uuid(), str)

        # uuid should be set by this startup process
        assert isinstance(test_discord_output.uuid, str)
        assert test_discord_output.get_uuid() == test_discord_output.uuid

        # Attempt to set the io_config_uuid
        uuid_test_str = "this is a bad uuid"
        test_discord_output.set_io_config_uuid(new_uuid=uuid_test_str)
        assert test_discord_output.get_io_config_uuid() == uuid_test_str

    @staticmethod
    def test_discord_output_produces_outputs() -> None:
        """
        Tests that the produced_inputs method produces a set of InputEvent derived classes.
        :return:
        """
        test_discord_output = DiscordOutput()
        outputs = test_discord_output.consumes_outputs()

        assert isinstance(outputs, set)

        for discord_input in outputs:
            assert issubclass(discord_input, OutputEvent)

    @pytest.mark.asyncio  # Need a running event loop to avoid warnings
    async def test_discord_output_status_method(self) -> None:
        """
        Directly tests the Input part of discord IO.
        :return:
        """
        test_discord_output = DiscordOutput()

        status_output = await test_discord_output.status()
        assert isinstance(status_output, str)
