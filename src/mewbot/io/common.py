# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Simple example elements which demonstrate some of the most basic mewbot objects.

This common elements are often used in various of the examples.
"""

from __future__ import annotations

from collections.abc import AsyncIterable
from typing import Any

import abc
from string import Template

from mewbot.api.v1 import Action, InputEvent, OutputEvent, Trigger


class AllEventsTrigger(Trigger):
    """
    Fires whenever there is an PostInputEvent.

    Will be used in the PrintBehavior.
    """

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """This trigger consumes all Input Events."""
        return {InputEvent}

    def matches(self, event: InputEvent) -> bool:
        """This trigger will always match - as this method always returns True."""
        return True


class PrintAction(Action):
    """
    Print every InputEvent.
    """

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """This action triggers on all InputEvents."""
        return {InputEvent}

    @staticmethod
    def produces_outputs() -> set[type[OutputEvent]]:
        """This action cannot produce any OutputEvents."""
        return set()

    async def act(self, event: InputEvent, state: dict[str, Any]) -> AsyncIterable[None]:
        """
        Just print every event which comes through - which should be all of them.

        This action should print any event the triggers match - used for debugging.
        :param event:
        :param state:
        :return:
        """
        print("Processed event", event)
        yield None


class EventWithReplyMixIn(abc.ABC, InputEvent):
    """
    Mix-in/protocol to mark an event has having the ability to be replied to.

    This is intended to aid the construction of multi-platform chatbots, by
    having the same actions being able to respond to events from different
    inputs in a platform-agnostic way.
    """

    @abc.abstractmethod
    def get_sender_name(self) -> str:
        """
        Returns the human friend name/nickname of the user who sent the event.
        """

    @abc.abstractmethod
    def get_sender_mention(self) -> str:
        """
        Returns the string contents required to mention/notify/ping the sender.

        If the reply methods will automatically ping the user, this may just be
        the human-readable username.
        """

    @abc.abstractmethod
    def prepare_reply(self, message: str) -> OutputEvent:
        """
        Creates an OutputEvent which is a reply to this input event.

        This event will be targeted at the same scope as the incoming message,
        e.g. in the same channel. It is expected that all people who saw the
        original message will also be able to see the reply.
        """

    @abc.abstractmethod
    def prepare_reply_narrowest_scope(self, message: str) -> OutputEvent:
        """
        Creates an OutputEvent which is a reply to this input event.

        This event will attempt to only be visible to a minimal number of
        people which still includes the person who sent the message.
        Note that for some systems, this may still be the original scope
        of all users who could see the original message.

        This function does not guarantee privacy, but is intended for use
        where replies are not relevant to other users, and thus can clutter
        up the main chat.
        """


class ReplyAction(Action):
    """
    Gives generic templated replies to any event with the Reply mix-in.

    The message can either be a simple static string, or be a template based
    on information from other actions. See the message setting for more details.
    """

    _message: Template
    _narrow_reply: bool = False

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """
        The reply action needs events that implement the reply protocol.
        """

        return {EventWithReplyMixIn}

    @staticmethod
    def produces_outputs() -> set[type[OutputEvent]]:
        """
        The reply action does not understand the event types, so we mark OutputEvent.
        """

        return {OutputEvent}

    @property
    def message(self) -> str:
        """
        The message format for replies to all events.

        The message format can either be a static string, or have placeholders
        that will be interpolated from information from the event or the previous
        actions.

        The two properties that are built in are `_username`, which will insert the
        username (nickname) of the user who sent the message we're replying to,
        and `_mention`, which will mention/ping/notify the user that we are replying.

        Examples:
            - Static message of "Hello, World!"
            - Greet a user with "Hello, $_user!"
            - Notify a user with "${_mention}, it's your turn to play!"

        For combining with actions that set state, you will need to look at what
        state information they set. For example, if we have an action that puts
        the time of the next calendar event into a variables called
        `next_event_name` and `next_event_time`, you might want to have a
        reply that looks like:

            "$_mention Coming up: $next_event_name starting at $next_event_time"
        """

        return self._message.template

    @message.setter
    def message(self, message: str) -> None:
        template = Template(message)

        if (
            hasattr(template, "is_valid")
            and not template.is_valid()  # pylint: disable=no-member
        ):
            raise ValueError("Message template is not valid")

        self._message = template

    @property
    def narrow_reply(self) -> bool:
        """
        Whether to send replies to the same scope or attempt to use a narrower scope.

        By default, replies are sent to the same scope as the message was received in.
        This could be the same channel in a messaging app, or the same thread is a forum
        like system.

        If narrow_reply is enabled, we attempt to reply to a narrower scope; for example
        the reply in a chat channel may be sent as a DM to the user. The only guarantees
        that is given is that the user will be able to see the message.

        A narrower reply does not mean that other people will not be able to see the message,
        and this functionality is provided to reduce the "SPAM-ness" of replies
        that are not relevant to other users. If you want to send actually private
        messages, you will need to use actions related to the specific IO you
        are using (e.g. Discord, Reddit, etc.)
        """

        return self._narrow_reply

    @narrow_reply.setter
    def narrow_reply(self, enabled: bool) -> None:
        self._narrow_reply = enabled

    async def act(
        self, event: InputEvent, state: dict[str, Any]
    ) -> AsyncIterable[OutputEvent]:
        """
        Reply to the received message.
        """

        if not isinstance(event, EventWithReplyMixIn):
            return

        message = self._message.safe_substitute(
            {
                "_user": event.get_sender_name(),
                "_mention": event.get_sender_mention(),
                **state,
            }
        )

        if self._narrow_reply:
            yield event.prepare_reply_narrowest_scope(message)
        else:
            yield event.prepare_reply(message)

    def __str__(self) -> str:
        """Explanation of this action."""

        return f"Reply to the message with '{self._message.template}'"
