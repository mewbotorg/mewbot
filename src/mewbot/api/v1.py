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
import uuid as system_uuid  # linter hack

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
    ManagerOutputEvent,
    IOConfigInterface,
    BotBase,
)
from mewbot.config import BehaviourConfigBlock, ConfigBlock


class Component(metaclass=ComponentRegistry):
    """
    The fundamnetal, registratable object for mewbot.
    If you want a class to be discoverable and displayable by the API, you should subclass this and
    add the necessary boilerplate to ComponentRegistry to handle registration (see the docs).
    """

    _id: str  # uuid for the component - you can set this, so it's deterministic at run time
    # But please consider not doing so - components with the same uuid are bad

    def serialise(self) -> ConfigBlock:
        """
        A ConfigBlock is a unit of YAML which represents this component.
        If you add any additional properties to a component, subclass this and add the new
        properties.
        :return:
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
        """
        Every component has to have an uuid.
        This uuid should be unique in the system.
        :return:
        """
        return self._id

    @uuid.setter
    def uuid(self, _id: str) -> None:
        if hasattr(self, "_id"):
            raise AttributeError("Can not set the ID of a component outside of creation")

        self._id = _id


@ComponentRegistry.register_api_version(ComponentKind.IOConfig, "v1")
class IOConfig(Component):
    """
    Define a service (or event source) that mewbot can connect to.
    """

    def set_io_config_uuids(self) -> None:
        """
        Iterates over the inputs and outputs, setting the io_config_uuid.
        """
        for _input in self.get_inputs():
            _input.set_io_config_uuid(self.uuid)

        for _output in self.get_outputs():
            _output.set_io_config_uuid(self.uuid)

    def get_uuid(self) -> str:
        """
        Needed, in addition to the property, to make static type checking happy
        (as properties can't be declared in the core.py definitions)
        :return:
        """
        return self.uuid

    @abc.abstractmethod
    def get_inputs(self) -> Sequence[Input]:
        """
        Return a sequence of all the Inputs defined in the IOConfig.
        """

    @abc.abstractmethod
    def get_outputs(self) -> Sequence[Output]:
        """
        Return a list of the outputs which this IOConfig supports
        :return:
        """

    async def accept_manager_output(self, manager_output: ManagerOutputEvent) -> bool:
        """
        Can this IOConfig process a manager request?
        """

    async def status(self) -> Dict[str, List[str]]:
        """
        Return a status object for this IOConfig.
        This object contains status information for the sub-objects this IOConfig holds.
        Keyed with, at least, "inputs" and "outputs"
        Valued with a list of string corresponding to this object.
        :return:
        """


class Input:
    """
    API definition for the Input classes
    Responsible for receiving input from the world and producing InputEvents
    """

    _id: str = str(system_uuid.uuid4())  # Can always be overridden later
    # If this input is part of an IOConfig, then this is it's uuid
    io_config_uuid: str = "Not set by parent IOConfig"

    queue: Optional[InputQueue]  # Queue for all Input events
    manager_trigger_data: Optional[Dict[str, Set[str]]]
    # If a manager is active, the data needed for the input to know if a command is manager or not
    manager_input_queue: Optional[
        ManagerInputQueue
    ]  # Send commands/info requests to the manager
    manager_output_queue: Optional[
        ManagerOutputQueue
    ]  # Receive commands/info requests from the manager

    def __init__(self) -> None:
        self.queue = None

    def bind(
        self,
        queue: InputQueue,
        manager_trigger_data: Optional[Dict[str, Set[str]]] = None,
        manager_input_queue: Optional[ManagerInputQueue] = None,
        manager_output_queue: Optional[ManagerOutputQueue] = None,
    ) -> None:
        """
        Add the bot queues to this input
        Which the bot uses to pass input events to the bot for processing.
        Optionally - sets up the manager interface - defines what is a manager command.
        Allows setting of the manager control and output queues
        :param queue: Put InputEvents on this queue
        :param manager_trigger_data:
                Data required to tell if an InputEvent is intended for the manager
        :param manager_input_queue:
                If an event is meant for the manager, use this queue to pass it on
        :param manager_output_queue:
                Receive events from the manager
                (in the current design, these are mostly info events to be sent back to
                the user)
        :return:
        """
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
        """
        Sets the Input running.
        :return:
        """

    async def status(self) -> str:
        """
        Provide some very basic info.
        If overriding this, you should probably include - at least - the uuid and io_config_uuid
        of this class.
        :return:
        """
        return (
            f"Input {self} - {self._id} - part of {self.io_config_uuid} - "
            f"does not have a status method."
        )

    @property
    def uuid(self) -> str:
        """
        Each element should have a unique uuid.
        Please.
        :return:
        """
        return self._id

    @uuid.setter
    def uuid(self, _id: str) -> None:
        """
        The uuid can only be set during the creation process.
        Attempts to set it afterwards will confue things mightily.
        :param _id:
        :return:
        """
        if hasattr(self, "_id"):
            raise AttributeError("Can not set the ID of an Input outside of creation")

        self._id = _id

    def get_uuid(self) -> str:
        """
        Needed because the api definitions do not support properties.
        :return:
        """
        return self._id

    def get_io_config_uuid(self) -> str:
        """
        Returns the uuid of the IOConfig this input is declared to be part of.
        :return:
        """
        return self.io_config_uuid

    def set_io_config_uuid(self, new_uuid: str) -> None:
        """
        Declare the uuid of the IOConfig this Input is a part of.
        :param new_uuid:
        :return:
        """
        self.io_config_uuid = new_uuid


class Output:
    """
    Base class for output methods - provides a method for the bot to output events
    in a particular way, with a particular config.
    """

    _id: str = str(system_uuid.uuid4())  # Can always be overridden later
    # If this input is part of an IOConfig, then this is it's uuid
    io_config_uuid: str = "Not set by parent IOConfig"

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
        :return : Did the message send successfully using this output.
        """

    async def status(self) -> str:
        """
        Generates a status string summarizing the status of this output.
        """

    @property
    def uuid(self) -> str:
        """
        Return a unique uuid for this Output.
        :return:
        """
        return self._id

    @uuid.setter
    def uuid(self, _id: str) -> None:
        """
        Block which prevents setting the uuid of an output outside creation.
        :param _id:
        :return:
        """
        if hasattr(self, "_id"):
            raise AttributeError("Can not set the ID of an Output outside of creation")

        self._id = _id

    def get_uuid(self) -> str:
        """
        Needed because cannot declare properties in the api definitions (e.g. v1.py)
        :return:
        """
        return self._id

    def get_io_config_uuid(self) -> str:
        """
        Unique uuid of the parent IOConfig
        :return:
        """
        return self.io_config_uuid

    def set_io_config_uuid(self, new_uuid: str) -> None:
        """
        Update the uuid of the IOConfig
        :param new_uuid:
        :return:
        """
        self.io_config_uuid = new_uuid


@ComponentRegistry.register_api_version(ComponentKind.Trigger, "v1")
class Trigger(Component):
    """
    The trigger is responsible for registering that a Behavior may wish to respond to
    an event.
    """

    @staticmethod
    @abc.abstractmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        InputClasses the trigger has registered an interest in.
        :return:
        """

    @abc.abstractmethod
    def matches(self, event: InputEvent) -> bool:
        """
        Returns True or False if the event is of interest to the Action.
        :param event:
        :return:
        """


@ComponentRegistry.register_api_version(ComponentKind.Condition, "v1")
class Condition(Component):
    """
    Variable conditions applied to input events after the Trigger
    Does the Action currently want to respond to events like that?
    """

    @staticmethod
    @abc.abstractmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        InputClasses the condition may trigger on.
        :return:
        """

    @abc.abstractmethod
    def allows(self, event: InputEvent) -> bool:
        """
        Returns True if the event can be processed and False otherwise.
        :param event:
        :return:
        """


@ComponentRegistry.register_api_version(ComponentKind.Action, "v1")
class Action(Component):
    @staticmethod
    @abc.abstractmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        """
        InputEvent classes of interest to this Action.
        :return:
        """

    @staticmethod
    @abc.abstractmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        """
        Output event classes which can be produced by this action.
        :return:
        """

    _queue: Optional[OutputQueue]

    def __init__(self) -> None:
        self._queue = None

    def bind(self, queue: OutputQueue) -> None:
        """
        Bind an OutputQueue to this action.
        :param queue:
        :return:
        """
        self._queue = queue

    async def send(self, event: OutputEvent) -> None:
        """
        Helper class to actually put events on the wire.
        Can be subclasses to handle detailed logging, other eventualities.
        :param event:
        :return:
        """
        if not self._queue:
            raise RuntimeError("Can not sent events before queue initialisation")

        await self._queue.put(event)

    @abc.abstractmethod
    async def act(self, event: InputEvent, state: Dict[str, Any]) -> None:
        """
        Ultimately responsible for transforming InputEvents into OutputEvents.
        :param event:
        :param state:
        :return:
        """


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
        """
        Return a status object for this behavior.
        Currently just a string - more sophistication will be added.
        :return:
        """


@ComponentRegistry.register_api_version(ComponentKind.Manager, "v1")
class Manager(Component):
    """
    Managers provide command and control for the bot
    """

    manager_input_queue: Optional[
        ManagerInputQueue
    ]  # Queue to communicate back to the manager
    manager_output_queue: Optional[ManagerOutputQueue]  # Queue to accept manager commands

    io_configs: List[IOConfigInterface]

    _managed_bot: BotBase

    def bind(self, in_queue: ManagerInputQueue, out_queue: ManagerOutputQueue) -> None:
        self.manager_input_queue = in_queue
        self.manager_output_queue = out_queue

    def set_bot(self, new_bot: BotBase) -> None:
        self._managed_bot = new_bot

    def get_bot(self) -> BotBase:
        return self._managed_bot

    def set_io_configs(self, io_configs: List[IOConfigInterface]) -> None:
        self.io_configs = io_configs

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
        """
        Start executing manager functions.
        :return:
        """

    @abc.abstractmethod
    async def process_manager_input_queue(self) -> None:
        """
        Take events off the manager input queue and process them.
        :return:
        """

    @abc.abstractmethod
    async def process_manager_output_queue(self) -> None:
        """
        Take events off the manager output queue and process them.
        :return:
        """

    @abc.abstractmethod
    async def status(self) -> Dict[str, Dict[str, Union[str, Dict[str, List[str]]]]]:
        """
        Provides a status object for this component - containing all the status strings for
        the subcomponents.
        Current a series of nested dicts.
        :return:
        """

    @abc.abstractmethod
    async def help(self) -> Dict[str, Dict[str, str]]:
        """
        Provide a help object - containing all the help data from all the components
        contained in this one.
        Currently, this object is a slightly hideous nested collection of dicts.
        :return:
        """


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
