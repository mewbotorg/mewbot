# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Test cases for the basic interface of the API v1 Behaviour class.
"""

# pylint: disable=too-few-public-methods

from __future__ import annotations

from typing import Any, AsyncIterable

import pytest

from mewbot.api.v1 import Action, Behaviour, Condition, InputEvent, OutputEvent, Trigger


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

    def test_create_behaviour(self) -> None:
        """Test creating a Behaviour with no Components."""

        behaviour = self.behaviour()

        assert behaviour.name == "Test"
        assert behaviour.active
        assert isinstance(behaviour.triggers, list) and not behaviour.triggers
        assert isinstance(behaviour.conditions, list) and not behaviour.conditions
        assert isinstance(behaviour.actions, list) and not behaviour.actions

    def test_disable_enable(self) -> None:
        """Test enabling and disabling a Behaviour."""

        behaviour = self.behaviour()

        assert behaviour.active
        behaviour.active = False
        assert not behaviour.active
        behaviour.active = True
        assert behaviour.active

        behaviour = self.behaviour(False)

        assert not behaviour.active
        behaviour.active = True
        assert behaviour.active
        behaviour.active = False
        assert not behaviour.active

    def test_serialise_behaviour(self) -> None:
        """Test exporting behaviour as configuration."""

        behaviour = self.behaviour()
        config = behaviour.serialise()

        assert config["kind"] == "Behaviour"
        assert config["implementation"] == "mewbot.api.v1.Behaviour"
        assert isinstance(config["properties"], dict)
        assert config["properties"] == {"active": True, "name": "Test"}
        assert isinstance(config["triggers"], list) and not config["triggers"]
        assert isinstance(config["conditions"], list) and not config["conditions"]
        assert isinstance(config["actions"], list) and not config["actions"]

    def test_create_add_invalid(self) -> None:
        """Test adding an invalid object to a behaviour."""

        behaviour = self.behaviour()

        with pytest.raises(TypeError):
            behaviour.add("")  # type: ignore

    def test_create_add_trigger(self) -> None:
        """Test adding an trigger to a behaviour."""

        behaviour = self.behaviour()
        trigger = TestBehaviour.trigger_generator({InputEvent})
        behaviour.add(trigger)

        assert behaviour.triggers == [trigger]
        assert isinstance(behaviour.conditions, list) and not behaviour.conditions
        assert isinstance(behaviour.actions, list) and not behaviour.actions

    def test_create_add_condition(self) -> None:
        """Test adding a condition to a behaviour."""

        class TestCondition(Condition):
            """Example condition for testing."""

            @staticmethod
            def consumes_inputs() -> set[type[InputEvent]]:
                return {InputEvent}

            def allows(self, event: InputEvent) -> bool:
                return True

        behaviour = self.behaviour()
        condition = TestCondition()
        behaviour.add(condition)

        assert isinstance(behaviour.triggers, list) and not behaviour.triggers
        assert behaviour.conditions == [condition]
        assert isinstance(behaviour.actions, list) and not behaviour.actions

    def test_create_add_action(self) -> None:
        """Test adding an action to a behaviour."""

        class TestAction(Action):
            """Example action for testing."""

            @staticmethod
            def consumes_inputs() -> set[type[InputEvent]]:
                return {InputEvent}

            @staticmethod
            def produces_outputs() -> set[type[OutputEvent]]:
                return {OutputEvent}

            async def act(
                self, event: InputEvent, state: dict[str, Any]
            ) -> AsyncIterable[OutputEvent]:
                yield OutputEvent()

        behaviour = self.behaviour()
        action = TestAction()
        behaviour.add(action)

        assert isinstance(behaviour.triggers, list) and not behaviour.triggers
        assert isinstance(behaviour.conditions, list) and not behaviour.conditions
        assert behaviour.actions == [action]

    @pytest.mark.parametrize("name,triggers,interests", BEHAVIOUR_MAP)
    def test_trigger_interests(
        self,
        name: str,
        triggers: list[set[type[InputEvent]]],
        interests: set[type[InputEvent]],
    ) -> None:
        """
        Tests for how Trigger's consume_input functions are resolved into Behaviour's interests.
        """

        behaviour = self.behaviour()

        for inputs in triggers:
            trigger = TestBehaviour.trigger_generator(inputs)
            behaviour.add(trigger)

        assert len(behaviour.triggers) == len(triggers), f"Incorrect triggers in {name}"
        assert behaviour.consumes_inputs() == interests, f"Incorrect triggers in {name}"

    @staticmethod
    def trigger_generator(events: set[type[InputEvent]]) -> Trigger:
        """Utility method for making a Trigger that consumes a given set of InputEvents."""

        class RequestedTrigger(Trigger):
            """Utility method for making a Trigger that consumes a given set of InputEvents."""

            @staticmethod
            def consumes_inputs() -> set[type[InputEvent]]:
                """Marks the given set of Events as accepted."""
                return events

            def matches(self, event: InputEvent) -> bool:
                """Match events from the given set."""
                return isinstance(event, tuple(events))

        return RequestedTrigger()

    @staticmethod
    def behaviour(active: bool = True) -> Behaviour:
        """Creates a Test Behaviour (without linting issues)."""
        # pylint: disable=unexpected-keyword-arg
        return Behaviour(name="Test", active=active)  # type: ignore
