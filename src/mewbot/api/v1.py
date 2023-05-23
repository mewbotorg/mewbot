#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Provides the v1 Component development API for MewBot.

This module provides abstract implementations of the MewBot Component protocols
which tie into the Registry system for automated Component discovery, and also
implement the YAML loading/serialising behaviour that is specified in the Loader
module.

Plugins that use this API will, therefore, be able to be automatically discovered
by bots, and have components states be preserved during a bot restart.
"""


from __future__ import annotations

import types
from collections.abc import AsyncIterable, Iterable
from typing import Any, Callable, TypeVar, Union, get_args, get_origin, get_type_hints

import abc
import functools

from mewbot.api.registry import ComponentRegistry
from mewbot.core import (
    ActionInterface,
    BehaviourConfigBlock,
    ComponentKind,
    ConditionInterface,
    ConfigBlock,
    InputEvent,
    InputQueue,
    OutputEvent,
    OutputQueue,
    TriggerInterface,
)


class Component(metaclass=ComponentRegistry):
    """
    The base class for all Components in the v1 implementation.

    The class uses the ComponentRegistry metaclass, so that all classes are
    automatically registered against an API type, and implements a serialise
    function that matches the behaviour of the loader in `mewbot.loader`.
    """

    _id: str

    def serialise(self) -> ConfigBlock:
        """
        Create a Loader compatible configuration block for this Component.

        The core information -- the component kind, implementation class, and
        UUID -- along with any class properties will be included in the information.
        """

        cls = type(self)

        kind, _ = ComponentRegistry.api_version(self)  # type: ignore

        output: ConfigBlock = {
            "kind": kind,
            "implementation": cls.__module__ + "." + cls.__qualname__,
            "uuid": self.uuid,
            "properties": {},
        }

        for prop in dir(cls):
            if not isinstance(getattr(cls, prop), property):
                continue

            if prop == "uuid":
                continue

            if getattr(cls, prop).fset:
                output["properties"][prop] = getattr(self, prop)

        return output

    @property
    def uuid(self) -> str:
        """The unique ID of this element."""

        return self._id

    @uuid.setter
    def uuid(self, _id: str) -> None:
        """The unique ID of this element."""

        if hasattr(self, "_id"):
            raise AttributeError("Can not set the ID of a component outside of creation")

        self._id = _id


@ComponentRegistry.register_api_version(ComponentKind.IOConfig, "v1")
class IOConfig(Component):
    """
    Configuration component that defines a service that mewbot can connect to.

    An IOConfig is a loadable component with configuration for interacting
    with an external system. The config provides :class:`~mewbot.api.v1.Input`
    and/or :class:`~mewbot.api.v1.Output` objects to the bot, which interact
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

    @abc.abstractmethod
    def get_inputs(self) -> Iterable[Input]:
        """
        Gets the Inputs that are used to read events from the service.

        These will be used in the current life cycle of the bot.
        If the bot is restarted, this method will be called again. It may return the same instances.

        :return: The Inputs that are used to read events from the service (if any)
        """

    @abc.abstractmethod
    def get_outputs(self) -> Iterable[Output]:
        """
        Gets the Outputs that are used to send events to the service.

        These will be used in the current life cycle of the bot.
        If the bot is restarted, this method will be called again. It may return the same instances.

        :return: The Outputs that are used to send events to the service (if any)
        """


class Input:
    """
    Class for reading from a service or other event source.

    Inputs connect to a system, ingest events in some way, and put them
    into the bot's input event queue for processing.
    """

    queue: InputQueue | None

    def __init__(self) -> None:
        self.queue = None

    @staticmethod
    @abc.abstractmethod
    def produces_inputs() -> set[type[InputEvent]]:
        """List the types of Events this Input class could produce."""

    def bind(self, queue: InputQueue) -> None:
        """Allows a Bot to attach the active input queue to this input."""

        self.queue = queue

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


class Output:
    """
    Class for performing read from a service.

    The bot's output processor takes events from the behaviours off
    the output queue, and passes it to all Outputs that declare that
    they can consume it.
    """

    @staticmethod
    @abc.abstractmethod
    def consumes_outputs() -> set[type[OutputEvent]]:
        """
        Defines the set of output events that this Output class can consume.

        :return: The types of event that will be processed.
        """

    @abc.abstractmethod
    async def output(self, event: OutputEvent) -> bool:
        """
        Does the work of transmitting the event to the world.

        :param: event The event to be transmitted
        :return: Whether the event was successfully transmitted.
        """


@ComponentRegistry.register_api_version(ComponentKind.Trigger, "v1")
class Trigger(Component):
    """
    A Trigger determines if a behaviour should be activated for a given event.

    A Behaviour is activated if any of its trigger conditions are met.

    Triggers should refrain from adding too many sub-clauses and conditions.
    Filtering behaviours is the role of the Condition Component.
    """

    @staticmethod
    @abc.abstractmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """
        The subtypes of InputEvent that this component accepts.

        This is used to save computational overhead by skipping events of the wrong type.
        Subclasses of the events specified here will also be processed.
        """

    @abc.abstractmethod
    def matches(self, event: InputEvent) -> bool:
        """Whether the event matches this trigger's activation condition."""


@ComponentRegistry.register_api_version(ComponentKind.Condition, "v1")
class Condition(Component):
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
    @abc.abstractmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """
        The subtypes of InputEvent that this component accepts.

        This is used to save computational overhead by skipping events of the wrong type.
        Subclasses of the events specified here will also be processed.
        """

    @abc.abstractmethod
    def allows(self, event: InputEvent) -> bool:
        """Whether the event is retained after passing through this filter."""


@ComponentRegistry.register_api_version(ComponentKind.Action, "v1")
class Action(Component):
    """
    Actions are executed when a Behaviour is Triggered, and meets all its Conditions.

    Actions are executed in order, and will do some combination of:
     - Interact with DataSource and DataStores
     - Emit OutputEvents to the queue
     - Add data to the state, which will be available to the other actions in the behaviour
    """

    @staticmethod
    @abc.abstractmethod
    def consumes_inputs() -> set[type[InputEvent]]:
        """
        The subtypes of InputEvent that this component accepts.

        This is used to save computational overhead by skipping events of the wrong type.
        Subclasses of the events specified here will also be processed.
        """

    @staticmethod
    @abc.abstractmethod
    def produces_outputs() -> set[type[OutputEvent]]:
        """
        The subtypes of OutputEvent that this component could generate.

        This may be checked by the bot to drop unexpected events.
        It may also be used to verify that the overall bot config has the required
        outputs to function as intended.
        """

    @abc.abstractmethod
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
        yield None  # pragma: nocover


@ComponentRegistry.register_api_version(ComponentKind.Behaviour, "v1")
class Behaviour(Component):
    """
    Behaviours connect InputEvents to OutputEvents and power a bot.

    Each behaviour has one or more Triggers and Actions, and zero or more Conditions.
    Whenever an Input emits an InputEvent, each Behaviour checks to see if one at least
    one Trigger matches the Event. If it does, it then checks that all the Conditions
    accept the Event. Assuming it does, the Actions for the Behaviour are executed in
    order, which can read from or write to DataStores, and emit OutputEvents.
    """

    # pylint: disable=too-many-instance-attributes
    # PyLint counts the private version (_name) and the getter (@property name) separately.
    # This causes it to see 9 attributes where there are only practically 6.

    _name: str = ""
    _active: bool = True
    _interests: set[type[InputEvent]]

    triggers: list[TriggerInterface]
    conditions: list[ConditionInterface]
    actions: list[ActionInterface]

    def __init__(self) -> None:
        """Initialises a new Behaviour."""
        self._interests = set()
        self.triggers = []
        self.conditions = []
        self.actions = []

    @property
    def name(self) -> str:
        """
        Returns the host this IOConfig will listen on.

        The port this IOConfig will listen is given by :meth port:.
        :return:
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = str(name)

    @property
    def active(self) -> bool:
        """
        Returns the host this IOConfig will listen on.

        The port this IOConfig will listen is given by :meth port:.
        :return:
        """
        return self._active

    @active.setter
    def active(self, active: bool) -> None:
        self._active = bool(active)

    @property
    def interests(self) -> frozenset[type[InputEvent]]:
        """
        Returns the set of InputEvent types this behaviour is interested in.
        """
        return frozenset(self._interests)

    def add(self, component: TriggerInterface | ConditionInterface | ActionInterface) -> None:
        """
        Adds a component to the behaviour which is one or more of a Tigger, Condition, or Action.

        The internal state of the behaviour will be updated, including the set of input
        event base types that will be handled.
        The order Actions are added in is preserved, allowing for chains using the state system.

        NOTE: The Registry forbids multiple API inheritance, but it is possible for classes
        from other ancestries to implement more than one of the interfaces.
        """

        if not isinstance(component, (TriggerInterface, ConditionInterface, ActionInterface)):
            raise TypeError(f"Component {component} is not a Trigger, Condition, or Action")

        if isinstance(component, TriggerInterface):
            self.triggers.append(component)
            self._update_interests(component)
        if isinstance(component, ConditionInterface):
            self.conditions.append(component)
        if isinstance(component, ActionInterface):
            self.actions.append(component)

    def _update_interests(self, trigger: TriggerInterface) -> None:
        """
        Updates the list of InputEvent base types that we are interested in.

        The event types from the new trigger are merged into the event set.
        """

        for possible_new_input in trigger.consumes_inputs():
            if possible_new_input in self._interests:
                continue

            removals = set()

            for existing_interest in self._interests:
                # If the new class is a subclass of an existing interest,
                # it is already part of our interests.
                if issubclass(possible_new_input, existing_interest):
                    break

                # If the new class is a supertype of an existing interest,
                # it replaces the existing one. Changing a set during iteration
                # leads to undefined results, we queue items for removal.
                if issubclass(existing_interest, possible_new_input):
                    removals.add(existing_interest)

            # If the new class is not in our current set, add it.
            else:
                self._interests = self._interests.difference(removals)
                self._interests.add(possible_new_input)

    def consumes_inputs(self) -> set[type[InputEvent]]:
        """
        The set of InputEvents which are acceptable to one or more triggers.

        Gets the list of base Input Event classes that the behaviour's triggers
        will accept. Subclasses of any class in this list will also be accepted.

        These events are not guaranteed to cause the Behaviour to be activated,
        but instead save processing overhead by pre-filtering events by their
        type without having to invoke the matching methods, which may be complex.
        """

        return self._interests

    async def process(self, event: InputEvent) -> AsyncIterable[OutputEvent]:
        """
        Processes an InputEvent.

        The Event is passed to all matching triggers; at least one must match
        Then the Event is passed to all conditions; they all must match

        If both of the above succeed, a state object is created, and the Event
        is passed to each action in turn, updating state and emitting any outputs.
        """
        if not any(trigger.matches(event) for trigger in self.triggers):
            return

        if not all(condition.allows(event) for condition in self.conditions):
            return

        state: dict[str, Any] = {}

        for action in self.actions:
            async for output in action.act(event, state):
                if output:
                    yield output

    def serialise(self) -> BehaviourConfigBlock:
        """
        Convert this Behaviour into a data object compatible with mewbot.loader.

        This extends the Component serialiser to include all triggers, conditions,
        and actions that implement the v1 APIs.
        Components from other ancestries are silently discarded.
        """

        config = super().serialise()

        # noinspection PyUnresolvedReferences
        return {
            "kind": config["kind"],
            "implementation": config["implementation"],
            "uuid": config["uuid"],
            "properties": config["properties"],
            "triggers": [x.serialise() for x in self.triggers if isinstance(x, Trigger)],
            "conditions": [
                x.serialise() for x in self.conditions if isinstance(x, Condition)
            ],
            "actions": [x.serialise() for x in self.actions if isinstance(x, Action)],
        }


TypingComponent = TypeVar("TypingComponent", bound=Union[Trigger, Condition])
TypingEvent = TypeVar("TypingEvent", bound=InputEvent)


def pre_filter_non_matching_events(
    wrapped: Callable[[TypingComponent, TypingEvent], bool]
) -> Callable[[TypingComponent, InputEvent], bool]:
    """
        Check an input event against the valid event types declared in the signature.

        Introspects the function to determine the types of InputEvent should be passed to it.
        Uses a decorator to check that the event being passed in is one of those.
            - If it is, the function is run
            - If it is not, False is returned

        Type guard exists to provide methods for run time typing validation.

    E.g. a decorator which checks that an InputEvent being passed to a function is of appropriate
         type.

    The intent of the tools here is to provide a more elegant alternative to constructs like

    .. code-block:: python

        def matches(self, event: InputEvent) -> bool:
            if not isinstance(event, DiscordMessageCreationEvent):
                return False
            [Function body]

    which could be found in a Trigger.

    Instead, using one of the decorators provided in this module, you might write


    .. code-block:: python

        @pre_filter_non_matching_events
        def matches(self, event: InputEvent) -> bool:
            [Function body]

    Or, as a more full example

    .. code-block:: python

        # Demo Code

        from mewbot.io.discord import DiscordInputEvent, DiscordUserJoinInputEvent
        from mewbot.io.http import IncomingWebhookEvent

        class A(Trigger):

            @staticmethod
            def consumes_inputs() -> set[type[InputEvent]]:
                return {DiscordInputEvent, IncomingWebhookEvent}

            @pre_filter_non_matching_events
            def matches(self, event: DiscordInputEvent | IncomingWebhookEvent) -> bool:
                return True

        print(A.matches) # <function A.matches at 0x7f6e703f4a40>
        print(A.matches.__doc__) # <function A.matches at 0x7f6e703f4a40>
        print(A().matches(InputEvent())) # False
        print(A().matches(DiscordInputEvent())) # True
        print(A().matches(DiscordUserJoinInputEvent("[some text]"))) # True

        :param wrapped:
        :return:
    """
    func_types = get_type_hints(wrapped)
    if "event" not in func_types:
        raise TypeError("Received function without 'event' parameter")

    # Flatten the type signature down to the unique InputEvent subclasses.
    event_types: tuple[type[TypingEvent]] = flatten_types(func_types["event"])

    bad_types = [
        t for t in event_types if not (isinstance(t, type) and issubclass(t, InputEvent))
    ]
    if bad_types:
        raise TypeError(
            (
                f"{wrapped.__qualname__}: "
                "Can not add filter for non-event type(s): "
                f"{' '.join([str(x) for x in bad_types])}"
            )
        )

    @functools.wraps(wrapped)
    def match_with_type_check(self: TypingComponent, event: InputEvent) -> bool:
        # noinspection PyTypeHints
        if not isinstance(event, event_types):
            return False

        return wrapped(self, event)

    return match_with_type_check


def flatten_types(event_types: type[TypingEvent]) -> tuple[type[TypingEvent]]:
    """
    Flattens a possible union of InputEvent types into a tuple of types.

    This is a helper method for pre_filter_non_matching_events.

    The types in the tuple are expected (but not guaranteed) to be InputEvent subtypes.
    This tuple can be safely used with isinstance() on all supported versions of Python.
    It can also be iterated to confirm all the types are actually InputEvents.
    """

    events: tuple[type[TypingEvent]]

    if isinstance(event_types, type):
        events = (event_types,)
    elif get_origin(event_types) is Union:
        events = get_args(event_types)
    elif isinstance(event_types, getattr(types, "UnionType")):
        events = get_args(event_types)
    else:  # pragma: no cover
        raise ValueError(
            "Got weird type from type hinting: " + event_types
        )  # pragma: no cover

    return events


__all__ = [
    "IOConfig",
    "Input",
    "Output",
    "Behaviour",
    "Trigger",
    "Condition",
    "Action",
    "InputEvent",
    "OutputEvent",
    "InputQueue",
    "OutputQueue",
    "pre_filter_non_matching_events",
]
