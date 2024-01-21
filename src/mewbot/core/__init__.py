#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
The core interface definitions for mewbot.

This module provides a set of types that can be checked at runtime, allowing
components to be developed.

This module contains:

 - Interfaces for IO components (IOConfig, Input, Output)
 - Interfaces for behaviours (Behaviour, Trigger, Condition, Action)
 - Base classes for OutputEvent, and type hints for the event queues.
 - Component helper, including an enum of component types and a mapping to the interfaces
 - TypedDict mapping to the YAML schema for components.
"""

from __future__ import annotations

from collections.abc import AsyncIterable, Iterable
from typing import Any, Protocol, TypedDict, Union, runtime_checkable

import asyncio
import dataclasses
import enum

from .input_events import InputEvent, InputEventProtocol


@dataclasses.dataclass
class OutputEvent:
    """
    Base class for all events accepted by :class:`~mewbot.core.OutputInterface`.

    :class:`~mewbot.core.Action`s (inside :class:`~mewbot.core.Behaviour`s)
    may emit output events via the :class:`~mewbot.core.EventQueue`

    This base event has no data or properties. Events must be immutable.
    """


InputQueue = asyncio.Queue[InputEvent]
OutputQueue = asyncio.Queue[OutputEvent]


@runtime_checkable
class IOConfigInterface(Protocol):
    """
    Configuration component that defines a service that mewbot can connect to.

    An IOConfig is a loadable component with configuration for interacting
    with an external system. The config provides :class:`~mewbot.core.InputInterface`
    and/or :class:`~mewbot.core.OutputInterface` objects to the bot, which interact
    with that system via the event queues.

    This class should be limited to configuration without an associated life
    cycle; it should not include short-lived tokens or active connections
    (which are the domain of the Input and Output instances this generates).

    For example, an IOConfig for a chat system would take a single set of
    login credentials, and provide an Input that logs in and waits for messages
    and an Output that sends messages.

    The Input and Output instances this class generate can either be generated
    once, or generated on request as part of the bot's lifecycle. Either way,
    they are passed to the bot via the `get_inputs` and `get_outputs` methods.
    """

    def get_inputs(self) -> Iterable[InputInterface]:
        """
        Gets the Inputs that are used to read events from the service.

        These will be used in the current life cycle of the bot.
        If the bot is restarted, this method will be called again. It may return the same instances.

        :return: The Inputs that are used to read events from the service (if any)
        """

    def get_outputs(self) -> Iterable[OutputInterface]:
        """
        Gets the Outputs that are used to send events to the service.

        These will be used in the current life cycle of the bot.
        If the bot is restarted, this method will be called again. It may return the same instances.

        :return: The Outputs that are used to send events to the service (if any)
        """


@runtime_checkable
class InputInterface(Protocol):
    """
    Class for reading from a service or other event source.

    Inputs connect to a system, ingest events in some way, and put them
    into the bot's input event queue for processing.
    """

    @staticmethod
    def produces_inputs() -> set[type[InputEvent]]:
        """List the types of Events this Input class could produce."""

    def bind(self, queue: InputQueue) -> None:
        """Allows a Bot to attach the active input queue to this input."""

    async def run(self) -> None:
        """
        Function called for this Input to interact with the service.

        The input should not attach to the service until this function is
        called.

        Notes:
         - This function will be run as an asyncio Task.
         - This function should be run after bind() is called.
         - This function may be run in a different loop to __init__.
        """


@runtime_checkable
class OutputInterface(Protocol):
    """
    Class for writing events out to a service.

    The bot's output processor takes events from the behaviours off
    the output queue, and passes it to all Outputs that declare that
    they can consume it.
    """

    @staticmethod
    def consumes_outputs() -> set[type[OutputEvent]]:
        """Defines the types of Event that this Output class can send."""

    async def output(self, event: OutputEvent) -> bool:
        """
        Send the given event to the service.

        :param: event The event to transmit.
        :return: Whether the event was successfully written.
        """


@runtime_checkable
class TriggerInterface(Protocol):
    """
    A Trigger determines if a behaviour should be activated for a given event.

    A Behaviour is activated if any of its trigger conditions are met.

    Triggers should refrain from adding too many sub-clauses and conditions.
    Filtering behaviours is the role of the Condition Component.
    """

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """
        The subtypes of InputEvent that this component accepts.

        This is used to save computational overhead by skipping events of the wrong type.
        Subclasses of the events specified here will also be processed.
        """

    def matches(self, event: InputEvent) -> bool:
        """Whether the event matches this trigger's activation condition."""


@runtime_checkable
class ConditionInterface(Protocol):
    """
    Filter for events being processed in a Behaviour.

    A Condition determines whether an event accepted by the Behaviour's
    Triggers will be passed to the Actions.

    Each condition makes its decision independently based on the InputEvent.
    The behaviour combines the results to determine if it should take the actions.

    Note that the bot implementation may 'fail-fast', and a condition may not
    see all events.
    """

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """
        The subtypes of InputEvent that this component accepts.

        This is used to save computational overhead by skipping events of the wrong type.
        Subclasses of the events specified here will also be processed.
        """

    def allows(self, event: InputEvent) -> bool:
        """Whether the event is retained after passing through this filter."""


@runtime_checkable
class ActionInterface(Protocol):
    """
    Actions are executed when a Behaviour is Triggered, and meets all its Conditions.

    Actions are executed in order, and will do some combination of:
     - Interact with DataSource and DataStores
     - Emit OutputEvents to the queue
     - Add data to the state, which will be available to the other actions in the behaviour
    """

    @staticmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """
        The subtypes of InputEvent that this component accepts.

        This is used to save computational overhead by skipping events of the wrong type.
        Subclasses of the events specified here will also be processed.
        """

    @staticmethod
    def produces_outputs() -> set[type[OutputEvent]]:
        """
        The subtypes of OutputEvent that this component could generate.

        This may be checked by the bot to drop unexpected events.
        It may also be used to verify that the overall bot config has the required
        outputs to function as intended.
        """

    async def act(
        self, event: InputEvent, state: dict[str, Any]
    ) -> AsyncIterable[OutputEvent | None]:
        """
        Performs the action.

        The event is provided, along with the state object from any actions
        that have already run for this event. Data added to or removed from
        `state` will be available for any further actions that process this event.
        No functionality is provided to prevent processing more actions.
        """
        yield OutputEvent()  # pragma: no cover (not reachable)


@runtime_checkable
class BehaviourInterface(Protocol):
    """
    Behaviours connect InputEvents to OutputEvents and power a bot.

    Each behaviour has one or more Triggers and Actions, and zero or more Conditions.
    Whenever an Input emits an InputEvent, each Behaviour checks to see if one at least
    one Trigger matches the Event. If it does, it then checks that all the Conditions
    accept the Event. Assuming it does, the Actions for the Behaviour are executed in
    order, which can read from or write to DataStores, and emit OutputEvents.
    """

    def add(self, component: TriggerInterface | ConditionInterface | ActionInterface) -> None:
        """
        Adds a component to the behaviour which is one or more of a Tigger, Condition, or Action.

        Note that the order of Actions being added must be preserved.
        """

    def consumes_inputs(self) -> set[type[InputEvent]]:
        """
        The set of InputEvents which are acceptable to one or more triggers.

        Gets the list of base Input Event classes that the behaviour's triggers
        will accept. Subclasses of any class in this list will also be accepted.

        These events are not guaranteed to cause the Behaviour to be activated,
        but instead save processing overhead by pre-filtering events by their
        type without having to invoke the matching methods, which may be complex.
        """

    async def process(self, event: InputEvent) -> AsyncIterable[OutputEvent]:
        """
        Processes an InputEvent.

        The Event is passed to all matching triggers; at least one must match
        Then the Event is passed to all conditions; they all must match

        If both of the above succeed, a state object is created, and the Event
        is passed to each action in turn, updating state and emitting any outputs.
        """
        yield OutputEvent()  # pragma: no cover (not reachable)


Component = Union[
    IOConfigInterface,
    TriggerInterface,
    ConditionInterface,
    ActionInterface,
    BehaviourInterface,
]


# pylint: disable=C0103
class ComponentKind(str, enum.Enum):
    """
    Enumeration of all the meta-types of Component.

    These are all the components that a bot is built out of.
    These all have a matching interface above (except for DataSource
    and Template which are not yet implemented, but in the specification)
    """

    Behaviour = "Behaviour"
    Trigger = "Trigger"
    Condition = "Condition"
    Action = "Action"
    IOConfig = "IOConfig"
    Template = "Template"
    DataSource = "DataSource"

    @classmethod
    def values(cls) -> list[str]:
        """List of named values."""

        return list(e for e in cls)

    @classmethod
    def interface(cls, value: ComponentKind) -> type[Component]:
        """Maps a value in this enum to the Interface for that component type."""

        _map: dict[ComponentKind, type[Component]] = {
            cls.Behaviour: BehaviourInterface,
            cls.Trigger: TriggerInterface,
            cls.Condition: ConditionInterface,
            cls.Action: ActionInterface,
            cls.IOConfig: IOConfigInterface,
        }

        if value in _map:
            return _map[value]

        raise ValueError(f"Invalid value {value}")


class ConfigBlock(TypedDict):
    """Common YAML Block for all components."""

    kind: str
    implementation: str
    uuid: str
    properties: dict[str, Any]


class BehaviourConfigBlock(ConfigBlock):
    """YAML block for a behaviour, which includes the subcomponents."""

    triggers: list[ConfigBlock]
    conditions: list[ConfigBlock]
    actions: list[ConfigBlock]


__all__ = [
    "ComponentKind",
    "Component",
    "IOConfigInterface",
    "InputInterface",
    "OutputInterface",
    "BehaviourInterface",
    "TriggerInterface",
    "ConditionInterface",
    "ActionInterface",
    "InputEvent",
    "InputEventProtocol",
    "OutputEvent",
    "InputQueue",
    "OutputQueue",
    "ConfigBlock",
    "BehaviourConfigBlock",
]
