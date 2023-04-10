# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests for the non-IO specific components.
"""

from __future__ import annotations

import dataclasses
import sys

import pytest

from mewbot.api.v1 import InputEvent
from mewbot.core import OutputEvent
from mewbot.io.common import AllEventTrigger, EventWithReplyMixIn, ReplyAction, PrintAction


class TestCommonIO:
    """
    Tests for the non-IO specific components.
    """

    def test_all_event_trigger(self) -> None:
        """
        Tests for the trigger that matches all input events.
        """

        trigger = AllEventTrigger()

        assert trigger.consumes_inputs() == {InputEvent}
        assert trigger.matches(InputEvent())

    async def test_print_output_action(self, capsys: pytest.CaptureFixture[str]) -> None:
        """
        Tests for the trigger that matches all input events.
        """

        action = PrintAction()

        assert action.consumes_inputs() == {InputEvent}
        assert action.produces_outputs() == set()

        actor = action.act(None, {})  # type: ignore
        assert await actor.__anext__() is None  # type: ignore
        with pytest.raises(StopAsyncIteration):
            await actor.__anext__()  # type: ignore

        captured_output = capsys.readouterr()
        assert captured_output.err == ""
        assert captured_output.out == "Processed event None\n"


@dataclasses.dataclass
class ReplyTestOutputEvent(OutputEvent):
    """Fake OutputEvent for testing ReplyAction."""

    message: str
    narrow: bool


class ReplyableTestEvent(EventWithReplyMixIn):
    """Fake InputEvent for testing ReplyAction."""

    def get_sender_name(self) -> str:
        """Test sender name (sender)."""

        return "sender"

    def get_sender_mention(self) -> str:
        """Test sender mention (sender)."""

        return "@sender#0000"

    def prepare_reply(self, message: str) -> OutputEvent:
        """Create a Test output even with the given message."""

        return ReplyTestOutputEvent(message, False)

    def prepare_reply_narrowest_scope(self, message: str) -> OutputEvent:
        """Create a Test output even with the given message."""

        return ReplyTestOutputEvent(message, True)


REPLY_MAP: list[tuple[str, bool, dict[str, str], str]] = [
    ("Hello, World!", False, {}, "Hello, World!"),
    ("Hello, World!", True, {}, "Hello, World!"),
    ("Hello, ${_user}!", False, {}, "Hello, sender!"),
]


class TestReplyEvents:
    """Tests for the ReplyAction."""

    def test_reply_action_statics(self) -> None:
        """Test statis methods on ReplyAction."""

        assert ReplyAction.consumes_inputs() == {EventWithReplyMixIn}
        assert ReplyAction.produces_outputs() == {OutputEvent}

    def test_create_action(self) -> None:
        """Creating the ReplyAction with not properties."""

        action = ReplyAction()
        assert not hasattr(action, "_message")
        assert action.narrow_reply is False

        with pytest.raises(AttributeError):
            assert action.message

    def test_create_action_with_message(self) -> None:
        """Creating the ReplyAction with a message template."""

        message = "Hello, World!"

        action = ReplyAction(message=message)  # type: ignore

        assert action.narrow_reply is False
        assert action.message == message
        assert str(action) == f"Reply to the message with '{message}'"

    @pytest.mark.skipif(
        sys.version_info <= (3, 11), reason="Check only supported on Python 3.11+"
    )
    def test_create_action_with_bad_template(self) -> None:
        """Creating the ReplyAction with a message template."""
        with pytest.raises(ValueError, match="Message template is not valid"):
            ReplyAction(message="$")  # type: ignore

    async def test_reply_bad_event(self) -> None:
        """Creating the ReplyAction with a message template."""

        action = ReplyAction()
        iterable = action.act(InputEvent(), {})

        with pytest.raises(StopAsyncIteration):
            await iterable.__anext__()  # type: ignore

    @pytest.mark.parametrize("message,narrow,state,reply", REPLY_MAP)
    async def test_reply(
        self, message: str, narrow: bool, state: dict[str, str], reply: str
    ) -> None:
        """Creating the ReplyAction with a message template."""

        action = ReplyAction(message=message, narrow_reply=narrow)  # type: ignore
        iterable = action.act(ReplyableTestEvent(), state)
        event = await iterable.__anext__()  # type: ignore

        assert isinstance(event, ReplyTestOutputEvent)
        assert event.message == reply
        assert event.narrow == narrow

        with pytest.raises(StopAsyncIteration):
            await iterable.__anext__()  # type: ignore
