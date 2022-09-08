#!/usr/bin/env python3

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
    ManagerInputQueue,
    ComponentKind,
    TriggerInterface,
    ConditionInterface,
    ActionInterface,
    ManagerOutputQueue,
    BotBase,
)
from mewbot.config import BehaviourConfigBlock, ConfigBlock


class Component(metaclass=ComponentRegistry):
    """Hello!"""

    _id: str

    def serialise(self) -> ConfigBlock:
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
        return self._id

    @uuid.setter
    def uuid(self, _id: str) -> None:
        if hasattr(self, "_id"):
            raise AttributeError("Can not set the ID of a component outside of creation")

        self._id = _id


@ComponentRegistry.register_api_version(ComponentKind.IOConfig, "v1")
class IOConfig(Component):
    """
    Define a service that mewbot can connect to.
    """

    @abc.abstractmethod
    def get_inputs(self) -> Sequence[Input]:
        ...

    @abc.abstractmethod
    def get_outputs(self) -> Sequence[Output]:
        ...

    async def status(self) -> Dict[str, List[str]]:
        pass


class Input:

    queue: Optional[InputQueue]  # Queue for all Input events
    manager_trigger_data: Optional[Dict[str, Set[str]]]
    # If a manager is active, the data needed for the input to know if a command is manager or not
    manager_input_queue: Optional[
        ManagerInputQueue
    ]  # Send commands/info requests to the manager
    manager_output_queue: Optional[
        ManagerOutputQueue
    ]  # Recieve commands/info requests from the manager

    def __init__(self) -> None:
        self.queue = None

    def bind(
        self,
        queue: InputQueue,
        manager_trigger_data: Optional[Dict[str, Set[str]]] = None,
        manager_input_queue: Optional[ManagerInputQueue] = None,
        manager_output_queue: Optional[ManagerOutputQueue] = None,
    ) -> None:
        self.queue = queue
        self.manager_trigger_data = manager_trigger_data
        self.manager_input_queue = manager_input_queue
        self.manager_output_queue = manager_output_queue

    @staticmethod
    def produces_inputs() -> Set[Type[InputEvent]]:
        """
        Defines the set of input events this Input class can produce.
        :return:
        """

    @abc.abstractmethod
    async def run(self) -> None:
        pass

    async def status(self) -> str:
        return f"{self} does not have a status method."


class Output:
    @staticmethod
    def consumes_outputs() -> Set[Type[OutputEvent]]:
        """
        Defines the set of output events that this Output class can consume
        :return:
        """

    async def output(self, event: OutputEvent) -> bool:
        """
        Does the work of transmitting the event to the world.
        :param event:
        :return:
        """

    async def status(self) -> str:
        pass


@ComponentRegistry.register_api_version(ComponentKind.Trigger, "v1")
class Trigger(Component):
    @staticmethod
    @abc.abstractmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        pass

    @abc.abstractmethod
    def matches(self, event: InputEvent) -> bool:
        pass


@ComponentRegistry.register_api_version(ComponentKind.Condition, "v1")
class Condition(Component):
    @staticmethod
    @abc.abstractmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        pass

    @abc.abstractmethod
    def allows(self, event: InputEvent) -> bool:
        pass


@ComponentRegistry.register_api_version(ComponentKind.Action, "v1")
class Action(Component):
    @staticmethod
    @abc.abstractmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        pass

    @staticmethod
    @abc.abstractmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        pass

    _queue: Optional[OutputQueue]

    def __init__(self) -> None:
        self._queue = None

    def bind(self, queue: OutputQueue) -> None:
        self._queue = queue

    async def send(self, event: OutputEvent) -> None:
        if not self._queue:
            raise RuntimeError("Can not sent events before queue initialisation")

        await self._queue.put(event)

    @abc.abstractmethod
    async def act(self, event: InputEvent, state: Dict[str, Any]) -> None:
        pass


@ComponentRegistry.register_api_version(ComponentKind.Behaviour, "v1")
class Behaviour(Component):
    name: str
    active: bool

    triggers: List[Trigger]
    conditions: List[Condition]
    actions: List[Action]

    interests: Set[Type[InputEvent]]

    def __init__(self, name: str, active: bool = True) -> None:
        self.name = name
        self.active = active

        self.interests = set()
        self.triggers = []
        self.conditions = []
        self.actions = []

    # noinspection PyTypeChecker
    def add(
        self, component: Union[TriggerInterface, ConditionInterface, ActionInterface]
    ) -> None:
        if not isinstance(component, (Trigger, Condition, Action)):
            raise TypeError(f"Component {component} is not a Trigger, Condition, or Action")

        # noinspection PyUnresolvedReferences
        interests = component.consumes_inputs()
        interests = self.interests.intersection(interests) if self.interests else interests

        if not interests:
            raise ValueError(
                f"Component {component} doesn't match input types {self.interests}"
            )

        self.interests = interests

        if isinstance(component, Trigger):
            self.triggers.append(component)
        if isinstance(component, Condition):
            self.conditions.append(component)
        if isinstance(component, Action):
            self.actions.append(component)

    def consumes_inputs(self) -> Set[Type[InputEvent]]:
        return self.interests

    def bind_output(self, output: OutputQueue) -> None:
        for action in self.actions:
            action.bind(output)

    async def process(self, event: InputEvent) -> None:
        if not any(True for trigger in self.triggers if trigger.matches(event)):
            return

        if not all(True for condition in self.conditions if condition.allows(event)):
            return

        state: Dict[str, Any] = {}

        for action in self.actions:
            await action.act(event, state)

    def serialise(self) -> BehaviourConfigBlock:
        config = super().serialise()

        return {
            "kind": config["implementation"],
            "implementation": config["implementation"],
            "uuid": config["uuid"],
            "properties": config["properties"],
            "triggers": [x.serialise() for x in self.triggers],
            "conditions": [x.serialise() for x in self.conditions],
            "actions": [x.serialise() for x in self.actions],
        }

    async def status(self) -> str:
        pass


@ComponentRegistry.register_api_version(ComponentKind.Manager, "v1")
class Manager(Component):

    manager_input_queue: Optional[
        ManagerInputQueue
    ]  # Queue to communicate back to the manager
    manager_output_queue: Optional[ManagerOutputQueue]  # Queue to accept manager commands
    _managed_bot: BotBase

    def bind(self, in_queue: ManagerInputQueue, out_queue: ManagerOutputQueue) -> None:
        self.manager_input_queue = in_queue
        self.manager_output_queue = out_queue

    def set_bot(self, new_bot: BotBase) -> None:
        self._managed_bot = new_bot

    def get_bot(self) -> BotBase:
        return self._managed_bot

    def get_trigger_data(self) -> Dict[str, Set[str]]:
        """
        Trigger data required by each of the individual inputs to tell if an incoming event is a
        command intended for the manager.
        """

    def get_in_queue(self) -> Optional[ManagerInputQueue]:
        """
        Returns the queue used to communicate commands/info requests/ etc. to the manager.
        """
        return self.manager_input_queue

    def get_out_queue(self) -> Optional[ManagerOutputQueue]:
        """
        Returns the
        """
        return self.manager_output_queue

    @abc.abstractmethod
    async def run(self) -> None:
        pass

    @abc.abstractmethod
    async def status(self) -> Dict[str, Dict[str, Union[str, Dict[str, List[str]]]]]:
        pass

    @abc.abstractmethod
    async def help(self) -> Dict[str, Dict[str, str]]:
        pass


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
    "Manager",
]
