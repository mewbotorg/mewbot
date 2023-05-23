# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests pre_filter_non_matching_events using a dummy Trigger.
"""

# pylint: disable=duplicate-code
# this is testing for identical behavior in two very similar cases
# duplication is inevitable

from typing import Union

import pytest

from mewbot.api.v1 import InputEvent, Trigger, pre_filter_non_matching_events
from mewbot.io.http import IncomingWebhookEvent
from mewbot.io.socket import SocketInputEvent

TYPE_ERROR_MESSAGE = r".*.matches: Can not add filter for non-event type\(s\): .*"


class SimpleTestTrigger(Trigger):
    """Testing Trigger - Single Event sub-type."""

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """
        Consume a specific type of Events.

        :return:
        """
        return {SocketInputEvent}

    @pre_filter_non_matching_events
    def matches(self, event: SocketInputEvent) -> bool:
        """
        If the event is of the right type, matches.

        :param event:
        :return:
        """
        return True


class UnionTestTrigger(Trigger):
    """
    Dummy trigger for testing.
    """

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """
        Consumes two radically different events.

        :return:
        """
        return {SocketInputEvent, IncomingWebhookEvent}

    @pre_filter_non_matching_events
    def matches(self, event: Union[SocketInputEvent, IncomingWebhookEvent]) -> bool:
        """
        If the event is of the right type, matches.

        :param event:
        :return:
        """
        return True


class PEP604TestTrigger(Trigger):
    """
    Dummy trigger for testing.
    """

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """
        Consumes two radically different events.

        :return:
        """
        return {SocketInputEvent, IncomingWebhookEvent}

    @pre_filter_non_matching_events
    def matches(self, event: SocketInputEvent | IncomingWebhookEvent) -> bool:
        """
        If the event is of the right type, matches.

        :param event:
        :return:
        """
        return True


class TestCheckInputEventAgainstSigTypesAnnotations:
    """
    Check the type guard annotation pre_filter_non_matching_events preforms as expected.
    """

    @pytest.mark.parametrize(
        "clazz", [SimpleTestTrigger, UnionTestTrigger, PEP604TestTrigger]
    )
    def test_match_on_base_input_event_fails_annotations(self, clazz: type[Trigger]) -> None:
        """
        Calls the decorated function with the base class for InputEvent.

        Should always fail.
        :return:
        """
        assert clazz().matches(InputEvent()) is False

    @pytest.mark.parametrize(
        "clazz", [SimpleTestTrigger, UnionTestTrigger, PEP604TestTrigger]
    )
    def test_match_two_of_two_valid_event_types_annotations(
        self, clazz: type[Trigger]
    ) -> None:
        """
        Tests that a valid event type does match - for IncomingWebhookEvent.

        :return:
        """
        test_socket_event = SocketInputEvent(data=b"some bytes")

        assert clazz().matches(test_socket_event) is True

    @pytest.mark.parametrize("clazz", [UnionTestTrigger, PEP604TestTrigger])
    def test_match_one_of_two_valid_event_types_annotations(
        self, clazz: type[Trigger]
    ) -> None:
        """
        Tests that a valid event type does match - for IncomingWebhookEvent.

        :return:
        """
        test_webhook_event = IncomingWebhookEvent(text="test_text")

        assert clazz().matches(test_webhook_event) is True

    @pytest.mark.parametrize(
        "clazz", [SimpleTestTrigger, UnionTestTrigger, PEP604TestTrigger]
    )
    def test_complete_the_wrong_class_in_as_an_event_annotations(
        self, clazz: type[Trigger]
    ) -> None:
        """
        Tests that the decorator raises a type error when we pass something complete wrong in.

        In place of an event
        :return:
        """
        try:
            clazz().matches(None)  # type: ignore
        except TypeError:
            pass
