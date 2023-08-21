# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests for the Console IO configuration.
"""

from typing import Type

import asyncio

import pytest

from mewbot.api.v1 import IOConfig
from mewbot.core import InputEvent, InputQueue
from mewbot.io.console import StandardConsoleInputOutput, ConsoleInputLine, ConsoleOutputLine
from mewbot.test import BaseTestClassWithConfig


class TestRSSIO(BaseTestClassWithConfig[StandardConsoleInputOutput]):
    """
    Tests for the RSS IO configuration.

    Load a bot with an RSSInput - this should yield a fully loaded RSSIO config.
    Which can then be tested.
    """

    config_file: str = "examples/console_io.yaml"
    implementation: Type[StandardConsoleInputOutput] = StandardConsoleInputOutput

    def test_check_class(self) -> None:
        """Confirm the configuration has been correctly loaded."""

        assert isinstance(self.component, StandardConsoleInputOutput)
        assert isinstance(self.component, IOConfig)
