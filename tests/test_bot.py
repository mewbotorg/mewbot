from typing import List

import asyncio

import pytest

from mewbot.bot import Bot, BotRunner
from mewbot.core import InputEvent, OutputEvent
from mewbot.manager import BasicManager

from tests.common import TestTools


class PoisonedBotRunner(BotRunner):
    """
    Calling run_forever tends to lose you control of execution.
    This must thus be prevented - for testing purposes.
    """

    @staticmethod
    def run_loop(program_loop: asyncio.AbstractEventLoop) -> None:
        """
        Terminate rather than starting the loop.
        :param program_loop:
        :return:
        """
        raise NotImplementedError

    def shutdown_tasks(
        self,
        loop: asyncio.AbstractEventLoop,
        input_task: asyncio.Task[None],
        output_task: asyncio.Task[None],
        other_tasks: List[asyncio.Task[None]],
    ) -> None:
        pass


class TestBot:
    """
    Preforms basic tests on the bot class.
    """

    @staticmethod
    def test_bot_init() -> None:

        test_bot = Bot(name="testbot - should not be running")
        assert isinstance(test_bot, Bot)

    @staticmethod
    def test_bot_everything_to_run() -> None:
        """
        Need to poison the bot runner to prevent it calling run_forever on the loop.
        :return:
        """
        test_bot = Bot(name="testbot - should not be running", runner=PoisonedBotRunner)
        try:
            test_bot.run()
        except NotImplementedError:
            pass

    @pytest.mark.asyncio
    async def test_process_input_queue(self) -> None:
        test_bot = Bot(name="testbot - should not be running", runner=PoisonedBotRunner)
        test_bot.build_runner()

        loop = asyncio.get_running_loop()
        loop.create_task(self.set_bot_shutdown(test_bot))

        await test_bot.runner.process_input_queue()

    @pytest.mark.asyncio
    async def test_process_output_queue(self) -> None:
        test_bot = Bot(name="testbot - should not be running", runner=PoisonedBotRunner)
        test_bot.build_runner()

        loop = asyncio.get_running_loop()
        loop.create_task(self.set_bot_shutdown(test_bot))

        await test_bot.runner.process_output_queue()

    @staticmethod
    async def call_stop_on_loop_with_delay() -> None:
        """
        Wait five seconds and call stop on the loop.
        """
        await asyncio.sleep(7)
        loop = asyncio.get_running_loop()
        loop.stop()

    @staticmethod
    async def set_bot_shutdown(test_bot: Bot) -> None:
        """
        Attempt to shut down the runner on a two seconds delay.
        :param test_bot:
        :return:
        """
        await asyncio.sleep(2)
        test_bot.runner.start_shutdown()


class TestBotRunner(TestTools):
    """
    Preform tests on the bot runner directly.
    """

    def test_bot_runner_init(self) -> None:
        """
        Tests starting up the BotRunner - with an optional manager.
        :return:
        """
        test_runner = PoisonedBotRunner(
            behaviours={}, inputs=set(), outputs={}, manager=BasicManager()
        )

        assert test_runner is not None

        test_runner.start_shutdown()

    def test_cannot_start_running_bot(self) -> None:
        """
        Tests that we cannot start a runner which is already running.
        :return:
        """
        test_runner = PoisonedBotRunner(
            behaviours={}, inputs=set(), outputs={}, manager=BasicManager()
        )

        assert test_runner is not None

        test_runner.note_startup()

        try:
            test_runner.run()
        except RuntimeError:
            pass

    @pytest.mark.asyncio
    async def test_prepare_loop_tasks(self) -> None:
        """
        Setup loop tasks for the trivial bot - shouldn't be too hard.
        :return:
        """
        test_runner = PoisonedBotRunner(
            behaviours={}, inputs=set(), outputs={}, manager=BasicManager()
        )

        assert test_runner is not None

        loop = asyncio.get_running_loop()

        input_task, _, _ = test_runner.prepare_loop_tasks(loop)

        input_task.cancel()

        # Should trigger the stop callback ... hopefully
        try:
            await input_task
        except asyncio.exceptions.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_prepare_then_shutdown_loop_tasks(self) -> None:
        """
        Setup loop tasks for the trivial bot - shouldn't be too hard.
        :return:
        """
        test_runner = PoisonedBotRunner(
            behaviours={}, inputs=set(), outputs={}, manager=BasicManager()
        )

        assert test_runner is not None

        loop = asyncio.get_running_loop()

        input_task, output_task, other_tasks = test_runner.prepare_loop_tasks(loop)

        test_runner.shutdown_tasks(
            loop=loop, input_task=input_task, output_task=output_task, other_tasks=other_tasks
        )

    @pytest.mark.asyncio
    async def test_run_setup_tasks_no_inputs(self) -> None:
        """
        Tests running setup_tasks without any inputs.
        :return:
        """
        test_runner = PoisonedBotRunner(
            behaviours={}, inputs=set(), outputs={}, manager=BasicManager()
        )

        assert test_runner is not None

        loop = asyncio.get_running_loop()

        test_runner.setup_tasks(loop)

    @pytest.mark.asyncio
    async def test_full_bot_setup_with_manager_and_poisoned_runner(self) -> None:
        """
        Tests fully setting up a managed bot - but with a BotRunner such that it
        cannot actually start.
        :return:
        """
        configured_bot = self.get_managed_discord_bot()

        configured_bot.runner_class = PoisonedBotRunner

        try:
            configured_bot.run()
        except NotImplementedError:
            pass

    @pytest.mark.asyncio
    async def test_full_bot_setup_without_manager_and_poisoned_runner(self) -> None:
        """
        Tests fully setting up a non-managed bot.
        Which is currently an option for increased
         - performance
         - security
        but at the cost of loosing all the features a manager offers.
        :return:
        """
        configured_bot = self.get_trivial_post_bot()

        configured_bot.runner_class = PoisonedBotRunner

        try:
            configured_bot.run()
        except NotImplementedError:
            pass

    @pytest.mark.asyncio
    async def test_cannot_set_bot_runner_directly(self) -> None:
        """
        Tests that the runner cannot be force set externally.
        :return:
        """
        # Prepare objects
        configured_bot = self.get_managed_discord_bot()
        poison_runner = PoisonedBotRunner(
            behaviours={}, inputs=set(), outputs={}, manager=BasicManager()
        )

        # Tests the runner attributes
        test_runner = None
        try:
            test_runner = configured_bot.runner
        except AttributeError:
            pass
        assert test_runner is None
        try:
            configured_bot.runner = poison_runner
        except AttributeError:
            pass

    @pytest.mark.asyncio
    async def test_processing_input_event_on_input_queue_managed_bot(self) -> None:
        """
        Build a bot
        Insert a dummy DiscordInputEvent into the queue.
        Run process_input_queue long enough to process it.
        (Also check for timeout).
        :return:
        """
        # Prepare objects
        configured_bot = self.get_trivial_post_bot()

        configured_bot.build_runner()
        test_input_event = InputEvent()

        configured_bot.runner.note_startup()

        # Inject event
        await configured_bot.runner.input_event_queue.put(test_input_event)

        # Run long enough to process
        try:
            await asyncio.wait_for(configured_bot.runner.process_input_queue(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

        # There should be no events left in the queue - run long enough to trigger timeout
        try:
            await asyncio.wait_for(configured_bot.runner.process_input_queue(), 7)
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_processing_output_event_on_output_queue_managed_bot(self) -> None:
        """
        Build a bot
        Insert a dummy DiscordInputEvent into the queue.
        Run process_input_queue long enough to process it.
        (Also check for timeout).
        :return:
        """
        # Prepare objects
        # This bot should respond to all input events
        configured_bot = self.get_trivial_post_bot()

        configured_bot.build_runner()
        test_output_event = OutputEvent()

        configured_bot.runner.note_startup()

        # Inject event
        await configured_bot.runner.output_event_queue.put(test_output_event)

        # Run long enough to process
        try:
            await asyncio.wait_for(configured_bot.runner.process_output_queue(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

        # There should be no events left in the queue - run long enough to trigger timeout
        try:
            await asyncio.wait_for(configured_bot.runner.process_output_queue(), 7)
        except asyncio.exceptions.TimeoutError:
            pass
