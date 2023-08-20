# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Test attempting to use the type guard for Triggers and Conditions in various invalid configurations.
"""

from __future__ import annotations

import types
import typing
from typing import Optional, Union

import pytest

from mewbot.api.v1 import pre_filter_non_matching_events
from mewbot.core import InputEvent
from mewbot.io.http import IncomingWebhookEvent
from mewbot.io.socket import SocketInputEvent

union_type: Optional[type] = getattr(types, "UnionType", None)

TYPE_ERROR_MESSAGE = r".*.matches: Can not add filter for non-event type\(s\): .*"


class TestCheckInputEventAgainstSigTypesAnnotations:
    """
    Check the type guard annotation check_input_event_against_sig_types preforms as expected.
    """

    def test_union_syntax_on_different_versions(self) -> None:
        """
        Probe annoyance where the union syntax seems to yield different results on 3.9 and 3.10.

        Preserved here as a canary for when a future version of python changes this behavior.
        Which will hopefully be soon.
        Either I'm missing something, or it's stupid.
        :return:
        """
        assert union_type is not None, "union_type was None - change to python syntax?"

        # This is not valid syntax in python 3.9 - so need to ignore it for mypy
        test_syntax_1 = SocketInputEvent | IncomingWebhookEvent
        # pylint: disable=isinstance-second-argument-not-valid-type
        assert isinstance(test_syntax_1, union_type)
        # pylint: disable=protected-access
        assert not isinstance(test_syntax_1, typing._UnionGenericAlias)  # type: ignore

        test_syntax_2 = Union[SocketInputEvent, IncomingWebhookEvent]
        # You would really hope this would work ... but, alas, it does not
        # pylint: disable=isinstance-second-argument-not-valid-type
        assert not isinstance(test_syntax_2, union_type)
        # pylint: disable=protected-access
        assert isinstance(test_syntax_2, typing._UnionGenericAlias)  # type: ignore

    def test_malformed_trigger_no_event_annotations(self) -> None:
        """
        Tests applying the decorator to a function without "event" as a possibility.

        :return:
        """
        with pytest.raises(TypeError, match="Received function without 'event' parameter"):

            @pre_filter_non_matching_events  # type: ignore
            def consumes_inputs() -> set[type[InputEvent]]:
                """
                Consumes two radically different events.

                :return:
                """
                return {SocketInputEvent, IncomingWebhookEvent}

    def test_malformed_trigger_bad_event_type_none_annotations(self) -> None:
        """
        Tests applying the decorator to a function without "event" as a possibility.

        :return:
        """

        with pytest.raises(TypeError, match=TYPE_ERROR_MESSAGE):

            @pre_filter_non_matching_events  # type: ignore
            def matches(event: None) -> bool:
                """
                If the event is of the right type, matches.

                :param event:
                :return:
                """
                return not event

    def test_malformed_trigger_bad_event_type_trigger_annotations(self) -> None:
        """
        Tests applying the decorator to a function without "event" as a possibility.

        :return:
        """
        with pytest.raises(
            TypeError,
            match=(
                r'(can only concatenate str \(not "int"\) to str|'
                r"Forward references must evaluate to types. Got 7.)"
            ),
        ):

            @pre_filter_non_matching_events  # type: ignore
            def matches(event: 7) -> bool:  # type: ignore
                """
                If the event is of the right type, matches.

                :param event:
                :return:
                """
                return not event

    def test_malformed_trigger_no_event_annotations2(self) -> None:
        """
        Tests applying the decorator to a function without "event" as a possibility.

        :return:
        """
        with pytest.raises(TypeError, match="Received function without 'event' parameter"):

            @pre_filter_non_matching_events  # type: ignore
            def consumes_inputs() -> set[type[InputEvent]]:
                """
                Consumes two radically different events.

                :return:
                """
                return {SocketInputEvent, IncomingWebhookEvent}

    def test_malformed_trigger_bad_event_type_none_annotations2(self) -> None:
        """
        Tests applying the decorator to a function without "event" as a possibility.

        :return:
        """
        with pytest.raises(TypeError, match=TYPE_ERROR_MESSAGE):

            @pre_filter_non_matching_events  # type: ignore
            def matches(event: None) -> bool:
                """
                If the event is of the right type, matches.

                :param event:
                :return:
                """
                return bool(event)

    def test_malformed_trigger_bad_event_type_trigger_annotations2(self) -> None:
        """
        Tests applying the decorator to a function without "event" as a possibility.

        :return:
        """
        with pytest.raises(TypeError, match=TYPE_ERROR_MESSAGE):

            @pre_filter_non_matching_events  # type: ignore
            def matches(event: object) -> bool:
                """
                If the event is of the right type, matches.

                :param event:
                :return:
                """
                return bool(event)
