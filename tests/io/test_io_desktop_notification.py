# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests for the desktop notification engine.
"""

from __future__ import annotations

from typing import Type

import asyncio

import pytest

from mewbot.test import BaseTestClassWithConfig

from mewbot.io.desktop_notification import (
    DesktopNotificationIO,
    DesktopNotificationOutputEngine,
    DesktopNotificationOutput,
    DesktopNotificationOutputEvent,
)
from mewbot.api.v1 import OutputEvent

# pylint: disable=R0903
#  Disable "too few public methods" for test cases - most test files will be classes used for
#  grouping and then individual tests alongside these


class TestDesktopNotification(BaseTestClassWithConfig[DesktopNotificationIO]):
    """
    Tests for the desktop notification engine.
    """

    config_file: str = "examples/discord_bots/discord_to_desktop_notification.yaml"
    implementation: Type[DesktopNotificationIO] = DesktopNotificationIO

    def test_check_class(self) -> None:
        """
        Tests for the desktop notification engine.
        """

        assert isinstance(self.component, DesktopNotificationIO)

        assert not self.component.get_inputs()
        assert self.component.get_outputs()

    def test_desktop_notification_output__init__(self) -> None:
        """
        Tests that we can start the DesktopNotificationOutput.
        """

        test_output = DesktopNotificationOutput()
        assert test_output is not None

        for input_type in test_output.consumes_outputs():
            assert issubclass(input_type, OutputEvent)

        outputs = self.component.get_outputs()
        assert isinstance(outputs, list)
        assert len(outputs) == 1

    @pytest.mark.asyncio
    async def test_desktop_notification_output_outputs(self) -> None:
        """
        Tests running a DesktopNotificationOutput.
        """

        test_output = DesktopNotificationOutput()

        test_event = DesktopNotificationOutputEvent(
            title="This is another test. Ignore it", text="This might be getting annoying"
        )

        # Run the input
        try:
            await asyncio.wait_for(test_output.output(test_event), 1)
        except asyncio.exceptions.TimeoutError:
            pass

    def test_desktop_notification_output_engine__init__(self) -> None:
        """
        Tests the DesktopNotificationOutputEngine.

        This is responsible for actually doing the
        work of producing desktop notification output.
        """

        test_engine = DesktopNotificationOutputEngine()
        assert test_engine is not None, "test_engine was, unexpectedly, None"

    def test_desktop_notification_output_engine_notify(self) -> None:
        """
        Tests that the DesktopNotificationOutputEngine has a notify method which can be called.
        """

        test_engine = DesktopNotificationOutputEngine()
        assert test_engine is not None, "test_engine was, unexpectedly, None"

        test_engine.notify(title="Ignore this message", text="This is a test")

    def test_desktop_notification_output_engine_notify_disable_enable(self) -> None:
        """
        Tests that the DesktopNotificationOutputEngine has a notify method which can be called.
        """

        test_engine = DesktopNotificationOutputEngine()
        assert test_engine is not None, "test_engine was, unexpectedly, None"

        test_engine.notify(title="Ignore this message", text="This is a test")

        test_engine.disable()

        test_engine.notify(title="Ignore this message", text="This is a test")

        assert test_engine.enabled is False
        try:
            setattr(test_engine, "enabled", True)  # Fool mypy into not complaining
        except AttributeError:
            pass
