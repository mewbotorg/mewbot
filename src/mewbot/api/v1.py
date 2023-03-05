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

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Union,
    Type,
)

import abc

from mewbot.api.registry import ComponentRegistry
from mewbot.core import (
    InputEvent,
    InputQueue,
    OutputEvent,
    OutputQueue,
    ComponentKind,
    TriggerInterface,
    ConditionInterface,
    ActionInterface,
    ConfigBlock,
    BehaviourConfigBlock,
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
    def get_inputs(self) -> Sequence[Input]:
        """
        Gets the Inputs that are used to read events from the service.

        These will be used in the current life cycle of the bot.
        If the bot is restarted, this method will be called again. It may return the same instances.

        :return: The Inputs that are used to read events from the service (if any)
        """

    @abc.abstractmethod
    def get_outputs(self) -> Sequence[Output]:
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

    queue: Optional[InputQueue]

    def __init__(self) -> None:
        self.queue = None

    @staticmethod
    @abc.abstractmethod
    def produces_inputs() -> Set[Type[InputEvent]]:
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
    def consumes_outputs() -> Set[Type[OutputEvent]]:
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
    def consumes_inputs() -> Set[Type[InputEvent]]:
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
    def consumes_inputs() -> Set[Type[InputEvent]]:
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
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        The subtypes of InputEvent that this component accepts.

        This is used to save computational overhead by skipping events of the wrong type.
        Subclasses of the events specified here will also be processed.
        """

    @staticmethod
    @abc.abstractmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        """
        The subtypes of OutputEvent that this component could generate.

        This may be checked by the bot to drop unexpected events.
        It may also be used to verify that the overall bot config has the required
        outputs to function as intended.
        """

    _queue: Optional[OutputQueue]

    def __init__(self) -> None:
        self._queue = None

    def bind(self, queue: OutputQueue) -> None:
        """
        Attaches the output to the bot's output queue.

        A queue processor will distribute output events put on this queue
        to the outputs that are able to process them.
        """

        self._queue = queue

    async def send(self, event: OutputEvent) -> None:
        """Helper method to send an event to the queue."""

        if not self._queue:
            raise RuntimeError("Can not sent events before queue initialisation")

        await self._queue.put(event)

    @abc.abstractmethod
    async def act(self, event: InputEvent, state: Dict[str, Any]) -> None:
        """
        Performs the action.

        The event is provided, along with the state object from any actions
        that have already run for this event. Data added to or removed from
        `state` will be available for any further actions that process this event.
        No functionality is provided to prevent processing more actions.
        """


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

    name: str
    active: bool

    triggers: List[TriggerInterface]
    conditions: List[ConditionInterface]
    actions: List[ActionInterface]

    interests: Set[Type[InputEvent]]

    def __init__(self, name: str, active: bool = True) -> None:
        """Initialises a new Behaviour."""

        self.name = name
        self.active = active

        self.interests = set()
        self.triggers = []
        self.conditions = []
        self.actions = []

    def add(
        self, component: Union[TriggerInterface, ConditionInterface, ActionInterface]
    ) -> None:
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
            if possible_new_input in self.interests:
                continue

            removals = set()

            for existing_interest in self.interests:
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
                self.interests = self.interests.difference(removals)
                self.interests.add(possible_new_input)

    def consumes_inputs(self) -> Set[Type[InputEvent]]:
        """
        The set of InputEvents which are acceptable to one or more triggers.

        Gets the list of base Input Event classes that the behaviour's triggers
        will accept. Subclasses of any class in this list will also be accepted.

        These events are not guaranteed to cause the Behaviour to be activated,
        but instead save processing overhead by pre-filtering events by their
        type without having to invoke the matching methods, which may be complex.
        """

        return self.interests

    def bind_output(self, output: OutputQueue) -> None:
        """
        Wrapper to bind the output queue to all actions in this behaviour.

        See :meth:`mewbot.core.ActionInterface:bind_output`
        """

        for action in self.actions:
            action.bind(output)

    async def process(self, event: InputEvent) -> None:
        """
        Processes an InputEvent.

        The Event is passed to all matching triggers; at least one must match
        Then the Event is passed to all conditions; they all must match

        If both of the above succeed, a state object is created, and the Event
        is passed to each action in turn, updating state and emitting any outputs.
        """

        if not any(True for trigger in self.triggers if trigger.matches(event)):
            return

        if not all(True for condition in self.conditions if condition.allows(event)):
            return

        state: Dict[str, Any] = {}

        for action in self.actions:
            await action.act(event, state)

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
]
