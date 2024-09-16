# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests pre_filter_non_matching_events using a dummy Trigger.
"""
import dataclasses

import pytest

from mewbot.core import InputEvent, InputEventProtocol
from mewbot.io.discord import DiscordMessageCreationEvent


class MessageInputEvent(InputEventProtocol):  # pylint: disable=too-few-public-methods
    """Example InputEventProtocol, requiring a message that is a string."""

    message: str


@dataclasses.dataclass
class DemoMessageInputEvent(InputEvent):
    """Example InputEvent, instances of which should match the MessageInputEvent protocol above."""

    message: str


class InitOnProtocol(InputEventProtocol):  # pylint: disable=too-few-public-methods
    """Example InputEventProtocol which as an `__init__` function."""

    def __init__(self) -> None:  # pylint: disable=super-init-not-called
        """
        This __init__ function should not be callable.

        It should be overridden by the InputEventProtocol's subclass hook.
        """


class TestProtocolTyping:
    """Test the InputEventProtocol system."""

    def test_cant_init(self) -> None:
        """Confirm you can not initialise InputEventProtocol subclasses."""
        with pytest.raises(RuntimeError):
            InitOnProtocol()

    def test_is_sub_class(self) -> None:
        """`InputEventProtocols` should be subclasses of InputEvents, but not of specific Events."""
        assert issubclass(MessageInputEvent, InputEventProtocol)
        assert issubclass(MessageInputEvent, InputEvent)
        assert not issubclass(MessageInputEvent, DiscordMessageCreationEvent)

    def test_is_instance(self) -> None:
        """Test isinstance() using InputEventProtocols."""

        event = InputEvent()

        assert isinstance(event, InputEvent)
        assert not isinstance(event, MessageInputEvent)

        event = DemoMessageInputEvent("hi")

        assert isinstance(event, InputEvent)
        assert isinstance(event, MessageInputEvent)

        event = DiscordMessageCreationEvent(text="hi", message={})  # type: ignore

        assert isinstance(event, InputEvent)
        assert not isinstance(event, MessageInputEvent)
