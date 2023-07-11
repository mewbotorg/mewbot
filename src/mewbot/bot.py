#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Contains the core class of mewbot - the Bot itself.

The objective of most other parts of this project is to produce a Bot, which can then interact with
the outside world.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Set, Type

import asyncio
import logging
import signal

from mewbot.core import (
    BehaviourInterface,
    InputEvent,
    InputInterface,
    InputQueue,
    IOConfigInterface,
    OutputEvent,
    OutputInterface,
    OutputQueue,
)
from mewbot.data import DataSource

logging.basicConfig(level=logging.INFO)


class Bot:
    """
    Fundamental object of mewbot - a collection of objects which forms a software bot.

    Everything else is tooling to construct and run (at least one) Bot.
    Contains all IOConfigs, Behaviours, DataSources e.t.c defined by the yaml specification for
    this bot.
    """

    name: str  # The bot's name
    _io_configs: List[IOConfigInterface]  # Connections to bot makes to other services
    _behaviours: List[BehaviourInterface]  # All the things the bot does
    _datastores: Dict[str, DataSource[Any]]  # Data sources and stores for this bot

    def __init__(self, name: str) -> None:
        """
        Basic bot startup.

        No subcomponents are present at this stage.
        They must be added later.
        Only the name of the bot is set at this point.
        :param name:
        """
        self.name = name
        self._io_configs = []
        self._behaviours = []
        self._datastores = {}

    def run(self) -> None:
        """
        Starts the bot processing events.

        This involves the creation of a :class BotRunner: instance, which will then be run.
        :return:
        """
        runner = BotRunner(
            self._marshal_behaviours(),
            self._marshal_inputs(),
            self._marshal_outputs(),
        )
        runner.run()

    def add_io_config(self, ioc: IOConfigInterface) -> None:
        """
        Add a :class IOConfig: to the Bot.

        This method should only be used _before_ the Bot is running.
        Calls to this method when the Bot is running may produce undefined behavior.
        :param ioc:
        :return:
        """
        self._io_configs.append(ioc)

    def add_behaviour(self, behaviour: BehaviourInterface) -> None:
        """
        Add a :class Behaviour: to the Bot.

        This should be only used _before_ the bot is running.
        Calls to this method when the Bot is running may produce undefined behavior.
        :param behaviour:
        :return:
        """
        self._behaviours.append(behaviour)

    def get_data_source(self, name: str) -> Optional[DataSource[Any]]:
        """
        Retrieve a :class DataSource: - by name - from the Bot's internal stores.

        Returns None if no :class DataSource: with that name is found.
        :param name:
        :return:
        """
        return self._datastores.get(name)

    def _marshal_behaviours(self) -> Dict[Type[InputEvent], Set[BehaviourInterface]]:
        behaviours: Dict[Type[InputEvent], Set[BehaviourInterface]] = {}

        for behaviour in self._behaviours:
            for event_type in behaviour.consumes_inputs():
                behaviours.setdefault(event_type, set()).add(behaviour)

        return behaviours

    def _marshal_inputs(self) -> Set[InputInterface]:
        inputs = set()

        for connection in self._io_configs:
            for con_input in connection.get_inputs():
                inputs.add(con_input)

        return inputs

    def _marshal_outputs(self) -> Dict[Type[OutputEvent], Set[OutputInterface]]:
        outputs: Dict[Type[OutputEvent], Set[OutputInterface]] = {}

        for connection in self._io_configs:
            for _output in connection.get_outputs():
                for event_type in _output.consumes_outputs():
                    outputs.setdefault(event_type, set()).add(_output)

        return outputs


class BotRunner:
    """
    Responsible for running this programs interaction with the world.

    The :class Bot: exists to marshall all information concerning its setup.
    It then initialises this class - which runs all the subcomponents of the bot.
    This class is responsible for all interactions of this program with the outside world.
    """

    input_event_queue: InputQueue
    output_event_queue: OutputQueue

    inputs: Set[InputInterface]
    outputs: Dict[Type[OutputEvent], Set[OutputInterface]] = {}
    behaviours: Dict[Type[InputEvent], Set[BehaviourInterface]] = {}

    _running: bool = False

    def __init__(
        self,
        behaviours: Dict[Type[InputEvent], Set[BehaviourInterface]],
        inputs: Set[InputInterface],
        outputs: Dict[Type[OutputEvent], Set[OutputInterface]],
    ) -> None:
        """
        Provides the runner with all information it should need to start.

        All sub-components of the bot should be passed in at this point.
        Adding additional parts later, once the runner has started, is not currently supported and
        will result in undefined behavior.
        If you wish to do this - and there is currently no inbuilt mechanism to do so - you must
        stop the bot, construct a new runner, and start it again.
        :param behaviours:
        :param inputs:
        :param outputs:
        """
        self.logger = logging.getLogger(__name__ + "BotRunner")

        self.input_event_queue = InputQueue()
        self.output_event_queue = OutputQueue()

        self.inputs = inputs
        self.outputs = outputs
        self.behaviours = behaviours

    def run(self, _loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """
        Start the bot at the end of construction.

        This will include, but may not be limited to
         - starting all input tasks - which listen for inputs using the various IOConfigs defined
           in the yaml blocks which compose this bot
         - adding the input handlers to enable this loop to gracefully shut down
        :param _loop:
        :return:
        """
        if self._running:
            raise RuntimeError("Bot is already running")

        loop = _loop if _loop else asyncio.get_event_loop()

        self.logger.info("Starting main event loop")
        self._running = True

        def stop(info: Optional[Any] = None) -> None:
            """
            Responsible for shutting down the loop and signalling that this bot has stopped.

            :param info: Optional - Why has stop been called?
            :return:
            """
            self.logger.warning("Stop called: %s", info)
            if self._running and loop.is_running():
                self.logger.info("Stopping loop run")
                loop.stop()
            self._running = False

        input_task = loop.create_task(self.process_input_queue())
        input_task.add_done_callback(stop)
        output_task = loop.create_task(self.process_output_queue())
        output_task.add_done_callback(stop)

        input_tasks = self.setup_tasks(loop)

        # Handle correctly terminating the loop
        self.add_signal_handlers(loop, stop)

        try:
            loop.run_forever()
        finally:
            # Stop accepting new events
            for task in input_tasks:
                if not task.done():
                    result = task.cancel()
                    self.logger.warning("Cancelling %s: %s", task, result)

            # Finish processing anything already in the queues.
            loop.run_until_complete(input_task)
            loop.run_until_complete(output_task)

    @staticmethod
    def add_signal_handlers(
        loop: asyncio.AbstractEventLoop,
        stop: Callable[
            [
                Optional[Any],
            ],
            None,
        ],
    ) -> None:
        """
        Add signal handlers to allow the loop to be gracefully stopped.

        (If this is possible - currently only possible on posix environments).
        :param loop:
        :param stop:
        :return:
        """
        try:
            loop.add_signal_handler(signal.SIGINT, stop)
        except NotImplementedError:
            # We're probably running on windows, where this is not an option
            pass
        try:
            loop.add_signal_handler(signal.SIGTERM, stop)
        except NotImplementedError:
            # We're probably running on windows, where this is not an option
            pass

    def setup_tasks(self, loop: asyncio.AbstractEventLoop) -> List[asyncio.Task[None]]:
        """
        Prepare all tasks to allow the bot to start.

        Tasks include, but may not be limited to, inputs, behaviors (and, through them) outputs.
        :param loop:
        :return:
        """
        input_tasks: List[asyncio.Task[None]] = []

        # Startup the inputs
        for _input in self.inputs:
            _input.bind(self.input_event_queue)
            self.logger.info("Starting input %s", _input)
            input_tasks.append(loop.create_task(_input.run()))

        return input_tasks

    async def process_input_queue(self) -> None:
        """
        Pulls events off the input queue.

        Matches events to the behaviors which can process them.
        Awaits the behaviour.process call to allow the behaviour time to respond to the event.
        :return:
        """
        while self._running:
            try:
                event = await asyncio.wait_for(self.input_event_queue.get(), 5)
            except asyncio.exceptions.TimeoutError:
                continue

            for event_type in self.behaviours:
                if not isinstance(event, event_type):
                    continue

                async_tasks = [
                    self._process_event_for_behaviour(behaviour, event)
                    for behaviour in self.behaviours[event_type]
                ]

                await asyncio.gather(*async_tasks)

    async def _process_event_for_behaviour(
        self, behaviour: BehaviourInterface, event: InputEvent
    ) -> None:
        async for output in behaviour.process(event):
            await self.output_event_queue.put(output)

    async def process_output_queue(self) -> None:
        """
        Consumes events off the output queue.

        Matches these events to the outputs which can handle events of that type.
        Calls the outputs' output method to transmit the contents of that message to the world.
        :return:
        """
        while self._running:
            try:
                event = await asyncio.wait_for(self.output_event_queue.get(), 5)
            except asyncio.exceptions.TimeoutError:
                continue

            for event_type in self.outputs:
                if isinstance(event, event_type):
                    for output in self.outputs[event_type]:
                        await output.output(event)
