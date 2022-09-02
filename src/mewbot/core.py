#!/usr/bin/env python3

"""
Interfaces for Components and Events to pass between them.
These interfaces are the minimum guarantees for the implementations,
which will be consistent between API versions.

We can only define methods in these interfaces and not properties.
If a property-like behaviour becomes necessary, we can use an abstract @property.
"""

from __future__ import annotations

from typing import Any, Dict, List, Protocol, Sequence, Set, Type, Union, runtime_checkable

import asyncio
import enum
import dataclasses


@dataclasses.dataclass
class InputEvent:
    pass


@dataclasses.dataclass
class OutputEvent:
    pass


InputQueue = asyncio.Queue[InputEvent]
OutputQueue = asyncio.Queue[OutputEvent]


@dataclasses.dataclass
class ManagerInputEvent:
    """
    Base class for input events flowing to the manager.
    Should (probably) not be used directly.
    """

    trigger_input_event: InputEvent


@dataclasses.dataclass
class ManagerOutputEvent:
    """fdfdsfdsfsf"""


@dataclasses.dataclass
class ManagerCommandInputEvent(ManagerInputEvent):
    """
    Base class for issuing commands to the manager.
    """


@dataclasses.dataclass
class ManagerInfoInputEvent(ManagerInputEvent):
    """
    Base class for passing information to the manager.
    May be information it has requested.
    """

    info_type: str = ""


ManagerInputQueue = asyncio.Queue[ManagerInputEvent]
ManagerOutputQueue = asyncio.Queue[ManagerOutputEvent]


@runtime_checkable
class IOConfigInterface(Protocol):
    def get_inputs(self) -> Sequence[InputInterface]:
        pass

    def get_outputs(self) -> Sequence[OutputInterface]:
        pass

    async def status(self) -> str:
        pass


@runtime_checkable
class InputInterface(Protocol):
    @staticmethod
    def produces_inputs() -> Set[Type[InputEvent]]:
        """
        Defines the set of input events this Input class can produce.
        """

    def bind(self, queue: InputQueue) -> None:
        pass

    async def run(self) -> None:
        pass


@runtime_checkable
class OutputInterface(Protocol):
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


@runtime_checkable
class TriggerInterface(Protocol):
    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        pass

    def matches(self, event: InputEvent) -> bool:
        pass


@runtime_checkable
class ConditionInterface(Protocol):
    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        pass

    def allows(self, event: InputEvent) -> bool:
        pass


@runtime_checkable
class ActionInterface(Protocol):
    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        pass

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        pass

    def bind(self, queue: OutputQueue) -> None:
        pass

    async def act(self, event: InputEvent, state: Dict[str, Any]) -> None:
        pass


@runtime_checkable
class BehaviourInterface(Protocol):
    def add(
        self, component: Union[TriggerInterface, ConditionInterface, ActionInterface]
    ) -> None:
        pass

    def consumes_inputs(self) -> Set[Type[InputEvent]]:
        pass

    def bind_output(self, output: OutputQueue) -> None:
        pass

    async def process(self, event: InputEvent) -> None:
        pass

    async def status(self) -> str:
        pass


@runtime_checkable
class ManagerInterface(Protocol):
    def bind(self, in_queue: ManagerInputQueue, out_queue: ManagerOutputQueue) -> None:
        pass

    async def status(self) -> Dict[str, Dict[str, str]]:
        pass

    async def help(self) -> Dict[str, Dict[str, str]]:
        pass


Component = Union[
    BehaviourInterface,
    IOConfigInterface,
    TriggerInterface,
    ConditionInterface,
    ActionInterface,
    ManagerInterface,
]


# pylint: disable=C0103
class ComponentKind(str, enum.Enum):
    Behaviour = "Behaviour"
    Trigger = "Trigger"
    Condition = "Condition"
    Action = "Action"
    IOConfig = "IOConfig"
    Template = "Template"
    DataSource = "DataSource"
    Manager = "Manager"

    @classmethod
    def values(cls) -> List[str]:
        return list(e for e in cls)

    @classmethod
    def interface(cls, value: ComponentKind) -> Type[Component]:
        _map: Dict[ComponentKind, Type[Component]] = {
            cls.Behaviour: BehaviourInterface,
            cls.Trigger: TriggerInterface,
            cls.Condition: ConditionInterface,
            cls.Action: ActionInterface,
            cls.IOConfig: IOConfigInterface,
            cls.Manager: ManagerInterface,
        }

        if value in _map:
            return _map[value]

        raise ValueError(f"Invalid value {value}")


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
    "ManagerInterface",
    "InputEvent",
    "OutputEvent",
    "ManagerInputEvent",
    "ManagerInputQueue",
    "InputQueue",
    "OutputQueue",
]
