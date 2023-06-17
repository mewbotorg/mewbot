# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Test cases for the process() logic of the API v1 Behaviour class.
"""

from __future__ import annotations

from typing import Any, AsyncIterable
import dataclasses

from mewbot.api.v1 import (
    Trigger,
    Behaviour,
    Condition,
    Action,
    InputEvent,
)
from mewbot.core import OutputEvent
from mewbot.io.common import EventWithReplyMixIn, ReplyAction


class ReplyTrigger(Trigger):
    """Trivial Trigger that accepts EventWithReplyMixIn Events."""

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """Accepts EventWithReplyMixIn Events."""
        return {EventWithReplyMixIn}

    def matches(self, event: InputEvent) -> bool:
        """Whether the event matches this trigger's activation condition."""
        return isinstance(event, EventWithReplyMixIn)


class ReplyableEvent(EventWithReplyMixIn):
    """InputEvent that supports the reply protocol."""

    def get_sender_name(self) -> str:
        """Test Reply -- stub for sender."""
        return "[[sender]]"

    def get_sender_mention(self) -> str:
        """Test Reply -- stub for sender."""
        return "[[sender mention]]"

    def prepare_reply(self, message: str) -> OutputEvent:
        """Test Reply -- generate a Reply event."""
        return Reply(message)

    def prepare_reply_narrowest_scope(self, message: str) -> OutputEvent:
        """Test Reply -- generate a Reply event."""
        return Reply(message)


class NullAction(Action):
    """Test Action that does nothing."""

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """Accept any kind of Event."""
        return {InputEvent}

    @staticmethod
    def produces_outputs() -> set[type[OutputEvent]]:
        """Output does nothing, so not outputs."""
        return set()

    async def act(self, event: InputEvent, state: dict[str, Any]) -> AsyncIterable[None]:
        """Yield nothing when acting."""
        yield None


class Sycophant(Condition):
    """'Sycophant' Condition, accepts all events."""

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """Accept any Event for checking."""
        return {InputEvent}

    def allows(self, event: InputEvent) -> bool:
        """Approve any Event."""
        return True


class Dissident(Condition):
    """'Dissident' Condition, denies all events."""

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """Accept any Event for checking."""
        return {InputEvent}

    def allows(self, event: InputEvent) -> bool:
        """Deny any Event."""
        return False


@dataclasses.dataclass
class Reply(OutputEvent):
    """Simple Text Reply Event."""

    message: str


class TestBehaviourProcess:
    """
    Test cases for the process() logic of the API v1 Behaviour class.
    """

    async def test_interests(self) -> None:
        """Test Registration of Interests with the test setup."""

        message = "Hello!"

        behaviour = self.create_behaviour(message)
        interests = behaviour.interests

        assert isinstance(interests, frozenset)
        assert len(interests) == 1
        assert interests == {EventWithReplyMixIn}

    async def test_process_trivial(self) -> None:
        """Test successfully processing an event with a Trigger."""

        message = "Hello!"

        behaviour = self.create_behaviour(message)
        events = [e async for e in behaviour.process(ReplyableEvent())]

        assert len(events) == 1
        assert isinstance(events[0], Reply)
        assert events[0].message == message

    async def test_process_unmatched_trigger(self) -> None:
        """Test successfully not-processing an event with no matched Trigger."""

        message = "Hello!"

        behaviour = self.create_behaviour(message)
        events = [e async for e in behaviour.process(InputEvent())]

        assert len(events) == 0

    async def test_process_allowed_condition(self) -> None:
        """Test successfully processing where allowed by a Condition."""

        message = "Hello!"

        behaviour = self.create_behaviour(message)
        behaviour.add(Sycophant())
        events = [e async for e in behaviour.process(ReplyableEvent())]

        assert len(events) == 1
        assert isinstance(events[0], Reply)
        assert events[0].message == message

    async def test_process_denied_condition(self) -> None:
        """Test successfully not-processing where denied by a Condition."""

        message = "Hello!"

        behaviour = self.create_behaviour(message)
        behaviour.add(Dissident())
        events = [e async for e in behaviour.process(ReplyableEvent())]

        assert len(events) == 0

    @staticmethod
    def create_behaviour(message: str) -> Behaviour:
        """Creates a Test Behaviour (without linting issues)."""

        # pylint: disable=unexpected-keyword-arg
        behaviour = Behaviour(name="Test")  # type: ignore
        behaviour.add(ReplyTrigger())
        behaviour.add(ReplyAction(message=message))  # type: ignore
        behaviour.add(NullAction())

        return behaviour
