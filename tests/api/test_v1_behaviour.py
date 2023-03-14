# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Test cases for the basic interface of the API v1 Behaviour class.
"""

from __future__ import annotations

from typing import Any

import pytest

from mewbot.api.v1 import Action, Behaviour, Condition, Trigger, InputEvent, OutputEvent


class EventAlpha(InputEvent):
    """Utility Event for Testing."""


class EventSubAlpha(EventAlpha):
    """Utility Event for Testing."""


class EventBeta(InputEvent):
    """Utility Event for Testing."""


class EventSubAlphaBeta(EventAlpha, EventBeta):
    """Utility Event for Testing."""


BEHAVIOUR_MAP: list[tuple[str, list[set[type[InputEvent]]], set[type[InputEvent]]]] = [
    ("Empty mapping", [], set()),
    ("Single trigger mapping, v1", [{InputEvent}], {InputEvent}),
    ("Single trigger mapping, v2", [{EventAlpha}], {EventAlpha}),
    ("Remapping same type", [{InputEvent}, {InputEvent}], {InputEvent}),
    ("Adding a sub-type", [{InputEvent}, {EventAlpha}], {InputEvent}),
    ("Adding a super-type", [{EventAlpha}, {InputEvent}], {InputEvent}),
    ("Adding two disjunct types", [{EventAlpha}, {EventBeta}], {EventAlpha, EventBeta}),
    ("Adding a sub-sub-type", [{InputEvent}, {EventSubAlpha}], {InputEvent}),
    ("Adding a super-super-type", [{EventSubAlpha}, {InputEvent}], {InputEvent}),
    ("Adding a sub-type", [{InputEvent, EventAlpha}], {InputEvent}),
    ("Adding a super-type", [{EventAlpha, InputEvent}], {InputEvent}),
    ("Adding two disjunct types", [{EventAlpha, EventBeta}], {EventAlpha, EventBeta}),
    ("Adding a sub-sub-type", [{InputEvent, EventSubAlpha}], {InputEvent}),
    ("Adding a super-super-type", [{EventSubAlpha, InputEvent}], {InputEvent}),
    (
        "Adding a super type to two types",
        [{EventAlpha, EventBeta}, {InputEvent}],
        {InputEvent},
    ),
    (
        "Adding a super type to two types",
        [{EventAlpha, EventBeta}, {EventSubAlphaBeta}],
        {EventAlpha, EventBeta},
    ),
]


class TestBehaviour:
    """Tests for the Behaviour clas in v1 of the API."""

    @staticmethod
    def test_create_behaviour() -> None:
        """Test creating a Behaviour with no Components."""

        behaviour = Behaviour("Test", True)

        assert behaviour.name == "Test"
        assert behaviour.active
        assert behaviour.triggers == []
        assert behaviour.conditions == []
        assert behaviour.actions == []

    @staticmethod
    def test_serialise_behaviour() -> None:
        """Test exporting behaviour as configuration."""

        behaviour = Behaviour("Test", True)
        config = behaviour.serialise()

        assert config["kind"] == "Behaviour"
        assert config["implementation"] == "mewbot.api.v1.Behaviour"
        assert config["properties"] == {}
        assert config["triggers"] == []
        assert config["conditions"] == []
        assert config["actions"] == []

    @staticmethod
    def test_create_add_invalid() -> None:
        """Test adding an invalid object to a behaviour."""

        behaviour = Behaviour("Test", True)

        with pytest.raises(TypeError):
            behaviour.add("")  # type: ignore

    @staticmethod
    def test_create_add_trigger() -> None:
        """Test adding an trigger to a behaviour."""

        behaviour = Behaviour("Test", True)
        trigger = TestBehaviour.trigger_generator({InputEvent})
        behaviour.add(trigger)

        assert behaviour.triggers == [trigger]
        assert behaviour.conditions == []
        assert behaviour.actions == []

    @staticmethod
    def test_create_add_condition() -> None:
        """Test adding a condition to a behaviour."""

        class TestCondition(Condition):
            @staticmethod
            def consumes_inputs() -> set[type[InputEvent]]:
                return {InputEvent}

            def allows(self, event: InputEvent) -> bool:
                return True

        behaviour = Behaviour("Test", True)
        condition = TestCondition()
        behaviour.add(condition)

        assert behaviour.triggers == []
        assert behaviour.conditions == [condition]
        assert behaviour.actions == []

    @staticmethod
    def test_create_add_action() -> None:
        """Test adding an action to a behaviour."""

        class TestAction(Action):
            @staticmethod
            def consumes_inputs() -> set[type[InputEvent]]:
                return {InputEvent}

            @staticmethod
            def produces_outputs() -> set[type[OutputEvent]]:
                return {OutputEvent}

            async def act(self, event: InputEvent, state: dict[str, Any]) -> None:
                pass

        behaviour = Behaviour("Test", True)
        action = TestAction()
        behaviour.add(action)

        assert behaviour.triggers == []
        assert behaviour.conditions == []
        assert behaviour.actions == [action]

    @staticmethod
    @pytest.mark.parametrize("name,triggers,interests", BEHAVIOUR_MAP)
    def test_trigger_interests(
        name: str, triggers: list[set[type[InputEvent]]], interests: set[type[InputEvent]]
    ) -> None:
        """
        Tests for how Trigger's consume_input functions are resolved into Behaviour's interests.
        """

        behaviour = Behaviour("Test", True)

        for inputs in triggers:
            trigger = TestBehaviour.trigger_generator(inputs)
            behaviour.add(trigger)

        assert len(behaviour.triggers) == len(triggers)
        assert behaviour.consumes_inputs() == interests

    @staticmethod
    def trigger_generator(events: set[type[InputEvent]]) -> Trigger:
        """Utility method for making a Trigger that consumes a given set of InputEvents."""

        class RequestedTrigger(Trigger):
            @staticmethod
            def consumes_inputs() -> set[type[InputEvent]]:
                return events

            def matches(self, event: InputEvent) -> bool:
                return True

        return RequestedTrigger()
