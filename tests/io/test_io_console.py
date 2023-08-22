# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

# pylint:disable=protected-access

"""
Tests for the Console IO configuration.
"""
from typing import TextIO, Type

import asyncio
import io
import os

import pytest

from mewbot.api.v1 import IOConfig
from mewbot.core import InputEvent
from mewbot.io.console import (
    ConsoleInputLine,
    ConsoleOutputLine,
    StandardConsoleInputOutput,
    StandardInput,
    StandardOutput,
)
from mewbot.test import BaseTestClassWithConfig


class TestRSSIO(BaseTestClassWithConfig[StandardConsoleInputOutput]):
    """
    Tests for the RSS IO configuration.

    Load a bot with an RSSInput - this should yield a fully loaded RSSIO config.
    Which can then be tested.
    """

    config_file: str = "examples/console_io_print.yaml"
    implementation: Type[StandardConsoleInputOutput] = StandardConsoleInputOutput

    def test_check_class(self) -> None:
        """Confirm the configuration has been correctly loaded."""

        assert isinstance(self.component, StandardConsoleInputOutput)
        assert isinstance(self.component, IOConfig)

    def test_get_inputs(self) -> None:
        """
        Checks the get_inputs method of the IOConfig.

        :return:
        """
        assert isinstance(self.component.get_inputs(), list)
        assert len(list(self.component.get_inputs())) == 1

        cand_input = list(self.component.get_inputs())[0]

        assert isinstance(cand_input, StandardInput)

    def test_get_outputs(self) -> None:
        """
        Checks the get_inputs method of the IOConfig.

        :return:
        """
        assert isinstance(self.component.get_outputs(), list)
        assert len(list(self.component.get_outputs())) == 1

        cand_output = list(self.component.get_outputs())[0]

        assert isinstance(cand_output, StandardOutput)

        assert isinstance(cand_output.consumes_outputs(), set)

    def test_inputs(self) -> None:
        """
        Checks the get_inputs method of the IOConfig.

        :return:
        """
        cand_input = list(self.component.get_inputs())[0]

        assert isinstance(cand_input, StandardInput)

        assert isinstance(cand_input.produces_inputs(), set)
        for cand_obj in cand_input.produces_inputs():
            assert issubclass(cand_obj, InputEvent)

    def test_console_input_line_methods(self) -> None:
        """
        Tests the ConsoleInputLineEvent input event.

        :return:
        """
        test_event = ConsoleInputLine(message="this is a test")
        assert test_event.message == "this is a test"

        assert isinstance(str(test_event), str)
        assert "this is a test" in str(test_event)

        assert isinstance(test_event.get_sender_name(), str)
        assert isinstance(test_event.get_sender_mention(), str)

        assert isinstance(test_event.prepare_reply("this is a thing"), ConsoleOutputLine)
        assert isinstance(
            test_event.prepare_reply_narrowest_scope("this is a thing"), ConsoleOutputLine
        )

    def test_console_output_line_methods(self) -> None:
        """
        Tests the ConsoleOutputLineEvent.

        :return:
        """
        test_output_event = ConsoleOutputLine(message="This is a test")
        assert test_output_event.message == "This is a test"

        assert isinstance(str(test_output_event), str), "rep should be a string"
        assert "This is a test" in str(test_output_event)

    @staticmethod
    async def _add_some_input(local_stdin: TextIO) -> None:
        await asyncio.sleep(0.5)
        local_stdin.write("Not sure this will work...\n")

    @pytest.mark.asyncio
    async def test_input_runs(self) -> None:
        """
        Tests that an input actually runs.

        :return:
        """

        cand_input = list(self.component.get_inputs())[0]

        assert isinstance(cand_input, StandardInput)

        # Replace the file handler in the class
        local_stdin = io.StringIO()
        cand_input.class_stdin = local_stdin

        await asyncio.wait_for(self._add_some_input(local_stdin), timeout=2)

        # pytest doesn't like trying to read from stdio during tests
        try:
            await asyncio.wait_for(cand_input.run(), timeout=2)
        except OSError:
            pass

        # Directly run the linux version - on Windows this should fail
        if os.name.lower() == "nt":
            try:
                await asyncio.wait_for(cand_input._linux_run(), timeout=2)
            except (AttributeError, asyncio.exceptions.TimeoutError):
                pass
        else:
            try:
                await asyncio.wait_for(cand_input._windows_run(), timeout=2)
            except OSError:
                pass

    @pytest.mark.asyncio
    async def test_output_runs(self) -> None:
        """
        Tests that an output actually runs...

        :return:
        """

        cand_output = list(self.component.get_outputs())[0]

        assert isinstance(cand_output, StandardOutput)

        test_event = ConsoleOutputLine(message="this is a test")

        # pytest doesn't like trying to read from stdio during tests
        await asyncio.wait_for(cand_output.output(event=test_event), timeout=2)
