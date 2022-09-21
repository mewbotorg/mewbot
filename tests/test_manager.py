# Loads a file in, sees if it works

from __future__ import annotations

from typing import Type, Dict, Set, List, Union, Tuple

import asyncio
import pytest

from tests.common import BaseTestClassWithConfig, TestTools

from mewbot.bot import Bot
from mewbot.core import (
    ManagerInputQueue,
    ManagerInfoInputEvent,
    InputEvent,
    ManagerInputEvent,
    ManagerOutputEvent,
    ManagerCommandInputEvent,
)
from mewbot.core import ManagerOutputQueue, ManagerInterface
from mewbot.manager import BasicManager


# pylint: disable=R0903
#  Disable "too few public methods" for test cases - most test files will be classes used for
#  grouping and then individual tests alongside these


class TestBotManager(BaseTestClassWithConfig[BasicManager], TestTools):
    config_file: str = "examples/discord_bots/trivial_discord_bot_managed.yaml"
    implementation: Type[BasicManager] = BasicManager

    def test_check_class(self) -> None:
        assert isinstance(self.component, BasicManager)

    def test_get_trigger_data(self) -> None:
        """
        Tests the get_trigger_data returns the expected data structure.
        Should be a dict of sets, keyed with strs and strings in the sets.
        """
        trigger_data: Dict[str, Set[str]] = self.component.get_trigger_data()

        assert isinstance(trigger_data, dict)

        for key in trigger_data.keys():
            assert isinstance(key, str)
            assert isinstance(trigger_data[key], set)
            for key_val in trigger_data[key]:
                assert isinstance(key_val, str)

    def test_manager_serialise(self) -> None:
        """
        Tests the serialise function of the manager - which converts it to a YAML
        block
        :return:
        """
        test_bot = Bot("Unconnected Bot for testing")
        self.component.set_bot(test_bot)

        self.component.serialise()

    def test_manager_set_io_configs(self) -> None:
        """
        Tests the manager set_io_configs method - just passing in an empty list.
        :return:
        """
        self.component.set_io_configs([])

    def test_manager_uuid(self) -> None:
        """
        Should have been read in and set from the manager definition YAML.
        :return:
        """
        assert self.component.uuid == "aaaaaaaa-aaaa-4aaa-0001-aaaaaaaaaa04"

        try:
            self.component.uuid = "new very bad uuid"
        except AttributeError:
            pass

    def test_strip_command_prefix(self) -> None:
        """
        Transforms the command input into a standard form to be accepted by the
        rest of the class.
        Might preform other normalisations - depends on the manager.
        """
        test_str = "status"
        assert test_str == self.component.strip_command_prefix(
            self.component.command_prefix + test_str
        )

    def test_can_access_bot_but_not_set_it(self) -> None:
        """
        You should be able to access the bot being managed through the bot property.
        But not set it using that property - have to use set_bot for that.
        """
        test_bot = Bot("Unconnected Bot for testing")
        self.component.set_bot(test_bot)

        assert test_bot == self.component.bot
        assert test_bot == self.component.get_bot()

        try:
            self.component.bot = test_bot
        except AttributeError:
            pass

    @pytest.mark.asyncio
    async def test_manager_status_and_render_status_trivial_bot(self) -> None:
        """
        Tests that the status method and render_status together produce a status str.
        """
        test_bot = Bot("Unconnected Bot for testing")
        self.component.set_bot(test_bot)

        manager_status: Dict[
            str, Dict[str, Union[str, Dict[str, List[str]]]]
        ] = await self.component.status()

        status_str = self.component.render_status(manager_status)

        assert isinstance(status_str, str)

    @pytest.mark.asyncio
    async def test_process_manager_iq_valid_io_queue_no_events(self) -> None:
        """
        Tests running the process_manager_input_queue function with a properly set
        input and output queue.
        There are no events on this queue.
        This should return immediately.
        """
        self.prep_component_with_bot_and_queues()

        # Set to 6 as the current timeout in the class is 5
        try:
            await asyncio.wait_for(self.component.process_manager_input_queue(), 6)
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_process_manager_iq_valid_io_input_event(self) -> None:
        """
        Tests running the process_manager_input_queue function with a properly set
        input and output queue.
        There are no events on this queue.
        This should return immediately.
        """
        test_input_queue, test_output_queue = self.prep_component_with_bot_and_queues()

        # This event should be processed
        valid_status_info_input: ManagerInputEvent = ManagerInfoInputEvent(
            info_type="!status",
            trigger_input_event=InputEvent(),
            io_config_src_uuid="not_a_uuid",
        )
        await test_input_queue.put(valid_status_info_input)

        # This event should be processed
        # But the system doesn't know how to handle it - so it should be ignored
        invalid_info_input: ManagerInputEvent = ManagerInfoInputEvent(
            info_type="!not_a_status_command_or_any_command",
            trigger_input_event=InputEvent(),
            io_config_src_uuid="not_a_uuid",
        )
        await test_input_queue.put(invalid_info_input)

        # There should be an event already in the queue - so the timeout does not matter
        try:
            await asyncio.wait_for(self.component.process_manager_input_queue(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

        # This event should be ignored - for now
        test_manager_cmd_input: ManagerCommandInputEvent = ManagerCommandInputEvent(
            trigger_input_event=InputEvent(), io_config_src_uuid="not a real uuid"
        )
        await test_input_queue.put(test_manager_cmd_input)

        # There should be an event already in the queue - so the timeout does not matter
        try:
            await asyncio.wait_for(self.component.process_manager_input_queue(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

        # There should be an event already in the queue - so the timeout does not matter
        try:
            await asyncio.wait_for(self.component.process_manager_input_queue(), 8)
        except asyncio.exceptions.TimeoutError:
            pass

        assert test_output_queue.qsize() == 1

    @pytest.mark.asyncio
    async def test_manager_command_event_ignored(self) -> None:

        test_input_queue, test_output_queue = self.prep_component_with_bot_and_queues()

        # This event should be ignored - for now
        test_manager_cmd_input: ManagerCommandInputEvent = ManagerCommandInputEvent(
            trigger_input_event=InputEvent(), io_config_src_uuid="not a real uuid"
        )
        await test_input_queue.put(test_manager_cmd_input)

        # There should be an event already in the queue - so the timeout does not matter
        try:
            await asyncio.wait_for(self.component.process_manager_input_queue(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

        assert test_output_queue.qsize() == 0

    @pytest.mark.asyncio
    async def test_bad_info_request_ignored(self) -> None:
        test_input_queue, test_output_queue = self.prep_component_with_bot_and_queues()

        # This event should be processed
        # But the system doesn't know how to handle it - so it should be ignored
        invalid_info_input: ManagerInputEvent = ManagerInfoInputEvent(
            info_type="!not_a_status_command_or_any_command",
            trigger_input_event=InputEvent(),
            io_config_src_uuid="not_a_uuid",
        )
        await test_input_queue.put(invalid_info_input)

        # There should be an event already in the queue - so the timeout does not matter
        try:
            await asyncio.wait_for(self.component.process_manager_input_queue(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

        assert test_output_queue.qsize() == 0

    @pytest.mark.asyncio
    async def test_process_manager_iq_valid_io_input_event_out_q_none(self) -> None:
        """
        Tests running the process_manager_input_queue function with a properly set
        input queue and an output queue set to None.
        There are no events on this queue.
        This should return immediately.
        """
        test_input_queue, test_output_queue = self.prep_component_with_bot_and_queues()

        self.component.manager_output_queue = None

        # This event should be processed
        test_manager_info_input: ManagerInputEvent = ManagerInfoInputEvent(
            info_type="!status",
            trigger_input_event=InputEvent(),
            io_config_src_uuid="not_a_uuid",
        )
        await test_input_queue.put(test_manager_info_input)

        # There should be an event already in the queue - so the timeout does not matter
        try:
            await asyncio.wait_for(self.component.process_manager_input_queue(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

        assert test_output_queue.qsize() == 0

    @pytest.mark.asyncio
    async def test_process_manager_iq_valid_io_input_event_valid_out_q(self) -> None:
        """
        Tests running the process_manager_input_queue function with a properly set
        input and output queue.
        There are input events in the queue.
        These should be processed by the input.
        And should be added to the output queue
        """
        test_input_queue, test_output_queue = self.prep_component_with_bot_and_queues()

        # This event should be processed
        test_status_info_input: ManagerInputEvent = ManagerInfoInputEvent(
            info_type="!status",
            trigger_input_event=InputEvent(),
            io_config_src_uuid="not_a_uuid",
        )
        await test_input_queue.put(test_status_info_input)

        # This event should be processed
        # But the system doesn't know how to handle it - so it should be ignored
        test_invalid_info_input: ManagerInputEvent = ManagerInfoInputEvent(
            info_type="!not_a_status_command_or_any_command",
            trigger_input_event=InputEvent(),
            io_config_src_uuid="not_a_uuid",
        )
        await test_input_queue.put(test_invalid_info_input)

        # This event should be ignored - for now
        test_manager_cmd_input: ManagerCommandInputEvent = ManagerCommandInputEvent(
            trigger_input_event=InputEvent(), io_config_src_uuid="not a real uuid"
        )
        await test_input_queue.put(test_manager_cmd_input)

        # There should be an event already in the queue - so the timeout does not matter
        try:
            await asyncio.wait_for(self.component.process_manager_input_queue(), 8)
        except asyncio.exceptions.TimeoutError:
            pass

        assert test_output_queue.qsize() == 1

    @pytest.mark.asyncio
    async def test_process_manager_iq_valid_io_input_event_then_out(self) -> None:
        """
        Tests running the process_manager_input_queue function with a properly set
        input and output queue.
        There are input events in the queue.
        These should be processed by the input.
        Then should be processed by the output
        """
        test_input_queue, test_output_queue = self.prep_component_with_bot_and_queues()

        # This event should be processed
        test_manager_info_input: ManagerInputEvent = ManagerInfoInputEvent(
            info_type="!status",
            trigger_input_event=InputEvent(),
            io_config_src_uuid="not_a_uuid",
        )
        await test_input_queue.put(test_manager_info_input)

        # There should be an event already in the queue - so the timeout does not matter
        try:
            await asyncio.wait_for(self.component.process_manager_input_queue(), 8)
        except asyncio.exceptions.TimeoutError:
            pass

        assert test_output_queue.qsize() == 1

        try:
            await asyncio.wait_for(self.component.process_manager_output_queue(), 8)
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_process_manager_iq_i_valid_o_none_input_event_then_out(self) -> None:
        """
        test process_manager_input_queue - valid input queue - output queue None
        - adds an input event - then allows it to process output events

        Tests running the process_manager_input_queue function with a properly set
        input and output queue.
        There are input events in the queue.
        These should be processed by the input.
        Then
        """

        test_input_queue, test_output_queue = self.prep_component_with_bot_and_queues()

        self.component.manager_output_queue = None

        # This event should be processed
        test_manager_info_input: ManagerInputEvent = ManagerInfoInputEvent(
            info_type="!status",
            trigger_input_event=InputEvent(),
            io_config_src_uuid="not_a_uuid",
        )
        await test_input_queue.put(test_manager_info_input)

        # There should be an event already in the queue - so the timeout does not matter
        try:
            await asyncio.wait_for(self.component.process_manager_input_queue(), 8)
        except asyncio.exceptions.TimeoutError:
            pass

        assert test_output_queue.qsize() == 0  # queue can't be written to

        try:
            await asyncio.wait_for(self.component.process_manager_output_queue(), 8)
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_process_manager_iq_i_none_o_none_input_event_then_out(self) -> None:
        """
        test process_manager_input_queue - input queue None - output queue None
        - adds an input event - then allows it to process output events

        Shouldn't do much.
        """

        self.prep_component_with_bot_and_queues()

        self.component.manager_input_queue = None
        self.component.manager_output_queue = None

        try:
            await asyncio.wait_for(self.component.process_manager_input_queue(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

        try:
            await asyncio.wait_for(self.component.process_manager_output_queue(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_output_to_all(self) -> None:
        """
        Tests trying to send a message to all points.
        At the moment, not implemented.
        """

        _, test_output_queue = self.prep_component_with_bot_and_queues()

        # Put an event for all points on the wire
        output_event: ManagerOutputEvent = ManagerOutputEvent(
            target_uuid="all", trigger_input_event=None
        )
        await test_output_queue.put(output_event)

        try:
            await asyncio.wait_for(self.component.process_manager_output_queue(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

    def prep_component_with_bot_and_queues(
        self,
    ) -> Tuple[ManagerInputQueue, ManagerOutputQueue]:
        """
        Add a bot and some queues to the component for further testing.
        """
        test_bot = Bot("Unconnected Bot for testing")
        self.component.set_bot(test_bot)

        test_input_queue: ManagerInputQueue = ManagerInputQueue()
        test_output_queue: ManagerOutputQueue = ManagerOutputQueue()

        self.component.bind(in_queue=test_input_queue, out_queue=test_output_queue)

        return test_input_queue, test_output_queue

    @pytest.mark.ascynio
    async def test_manager_status(self) -> None:

        managed_bot = self.get_managed_discord_bot()

        self.component.set_bot(new_bot=managed_bot)

        status_dict = await self.component.status()
        assert isinstance(status_dict, dict)


class TestUnboundManagerInit:
    @staticmethod
    def test_manager_without_queue_bindings() -> None:
        test_manager: ManagerInterface = BasicManager()

        # No queues have been set up - so this should be as is
        try:
            assert test_manager.get_in_queue() is None
        except AttributeError:
            pass
        try:
            assert test_manager.get_out_queue() is None
        except AttributeError:
            pass
