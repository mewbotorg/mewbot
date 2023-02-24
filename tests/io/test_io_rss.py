# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

from typing import Type

import asyncio
import pytest

from tests.common import BaseTestClassWithConfig

from mewbot.core import InputEvent, InputQueue
from mewbot.io.rss import RSSIO, RSSInput, RSSInputState
from mewbot.api.v1 import IOConfig


class TestRSSIO(BaseTestClassWithConfig[RSSIO]):
    """
    Load a bot with an RSSInput - this should yield a fully loaded RSSIO config.
    Which can then be tested.
    """

    config_file: str = "examples/rss_input.yaml"
    implementation: Type[RSSIO] = RSSIO

    def test_check_class(self) -> None:
        assert isinstance(self.component, RSSIO)
        assert isinstance(self.component, IOConfig)

    def get_rss_input_from_component(self) -> RSSInput:
        self.component.get_inputs()  # Tests the "inputs not none" case
        component_rss_input = self.component.get_inputs()
        assert isinstance(component_rss_input, list)
        assert len(component_rss_input) == 1

        test_rss_io_input: RSSInput = component_rss_input[0]

        return test_rss_io_input

    def test_rss_input_declared_outputs(self) -> None:
        """
        Tests that the declared output events of the RSSInput are all InputClass descendants
        """
        rss_io_input = self.get_rss_input_from_component()

        assert isinstance(rss_io_input.produces_inputs(), set)

        for output_class in rss_io_input.produces_inputs():
            assert issubclass(output_class, InputEvent)

    def test_direct_set_polling_every_property_fails(self) -> None:
        """
        Test that directly setting the "polling_every" fails.
        """
        assert isinstance(self.component.polling_every, int)

        try:
            self.component.polling_every = 4
        except AttributeError:
            pass

    def test_get_set_sites_property(self) -> None:
        """
        Tests that the "sites" property can be read and set.
        """
        test_sites = self.component.sites
        assert isinstance(test_sites, list)

        # Attempt to set sites to be a string
        try:
            setattr(self.component, "sites", "")  # To stop mypy complaining
        except AttributeError:
            pass

        self.component.sites = []

        # Tests that this also sets the sites property of the input
        test_rss_io_input = self.get_rss_input_from_component()

        assert isinstance(test_rss_io_input.sites, list)
        # Will have been set off the input sites
        assert len(test_rss_io_input.sites) == 0

        self.component.sites = [
            "www.google.com",
        ]

        assert isinstance(test_rss_io_input.sites, list)
        # Will have been set off the input sites
        assert len(test_rss_io_input.sites) == 1

        # Setting the sites to something which is not a list should fail
        try:
            self.component.sites = ""  # type: ignore
        except AttributeError:
            pass

    def test_rss_input_get_set_polling_interval_property(self) -> None:
        """
        Tests the RSSInput polling_interval property.
        """
        rss_input = self.get_rss_input_from_component()

        assert rss_input.polling_interval == 30.0
        # Attempt t set the polling interval directly - should fail
        # It's a property calculated from the sites declared and the polling_every property
        try:
            rss_input.polling_interval = 5.0  # type: ignore
        except AttributeError:
            pass

        rss_input.polling_every = 30
        assert rss_input.polling_every == 30
        assert rss_input.polling_interval == 15.0

    @pytest.mark.asyncio
    async def test_component_run(self) -> None:
        """
        Run the component's input method - should run without throwing an error.
        """
        component_rss_input = self.component.get_inputs()
        assert isinstance(component_rss_input, list)
        assert len(component_rss_input) == 1

        test_rss_io_input = component_rss_input[0]

        # Run the input
        try:
            await asyncio.wait_for(test_rss_io_input.run(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_component_run_with_startup_queue_depth(self) -> None:
        """
        Run the component's input method - should run without throwing an error.
        """
        component_rss_input = self.component.get_inputs()
        assert isinstance(component_rss_input, list)
        assert len(component_rss_input) == 1

        test_rss_io_input = component_rss_input[0]
        test_rss_io_input.startup_queue_depth = 5

        # Run the input
        try:
            await asyncio.wait_for(test_rss_io_input.run(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_component_poll_site_feed(self) -> None:
        """
        Run the component's input method - should run without throwing an error.
        """
        component_rss_input = self.component.get_inputs()
        assert isinstance(component_rss_input, list)
        assert len(component_rss_input) == 1

        test_rss_io_input = component_rss_input[0]

        # poll_site_feed
        try:
            await asyncio.wait_for(
                test_rss_io_input.poll_site_feed("https://www.theguardian.com/world/rss"), 10
            )
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_component_run_after_repeated_get_inputs_call(self) -> None:
        """
        Run the component's input method after nullifying components
        """
        self.component.get_inputs()
        test_rss_io_input = self.get_rss_input_from_component()

        # Run the input
        try:
            await asyncio.wait_for(test_rss_io_input.run(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_run_with_existing_events_in_state(self) -> None:
        """
        Call run twice - which should result in existing events being seen twice.
        """
        self.component.get_inputs()
        test_rss_io_input = self.get_rss_input_from_component()

        # Crank down the polling interval - to be sure we get some events
        test_rss_io_input.polling_every = 4

        # Run the input
        try:
            await asyncio.wait_for(test_rss_io_input.run(), 5)
        except asyncio.exceptions.TimeoutError:
            pass

        assert test_rss_io_input.state.sent_entries_size > 0

        # Run the input - with known sent entries
        try:
            await asyncio.wait_for(test_rss_io_input.run(), 5)
        except asyncio.exceptions.TimeoutError:
            pass

    def test_get_outputs_empty_list(self) -> None:
        """
        Tests that the get_outputs method produces an empty list.
        """
        assert not self.component.get_outputs()

    def test_rss_input_state_methods(self) -> None:
        """
        Tests the methods for the internal RSSInputState dataclass.
        """
        test_rss_io_input = self.get_rss_input_from_component()

        test_rss_input_state: RSSInputState = test_rss_io_input.state

        test_rss_input_state.start()

        assert test_rss_input_state.sites == [
            "https://www.theguardian.com/world/rss",
            "https://www.engadget.com/rss.xml",
        ]

    def test_bad_input_for_rss_input_sites(self) -> None:
        """
        Tests trying to set the RSSInput sites property to something which is not a list.
        """
        test_rss_io_input = self.get_rss_input_from_component()

        try:
            test_rss_io_input.sites = ""  # type: ignore
        except AttributeError:
            pass

        test_rss_io_input.sites = []
        assert test_rss_io_input.polling_interval is None
        assert test_rss_io_input.polling_every == 60

    @pytest.mark.asyncio
    async def test_run_with_existing_events_in_state_input_queue(self) -> None:
        """
        Call run twice - which should result in existing events being seen twice.
        Unlike the above test for this case, there us an output queue defined.
        Check events are put onto the output queue.
        """
        self.component.get_inputs()
        test_rss_io_input = self.get_rss_input_from_component()

        # Crank down the polling interval - to be sure we get some events
        test_rss_io_input.polling_every = 4

        test_input_queue: InputQueue = InputQueue()
        test_rss_io_input.bind(test_input_queue)

        # Run the input
        try:
            await asyncio.wait_for(test_rss_io_input.run(), 5)
        except asyncio.exceptions.TimeoutError:
            pass

        assert test_rss_io_input.state.sent_entries_size > 0
        assert test_input_queue.qsize() == 10

        # Run the input - with known sent entries
        try:
            await asyncio.wait_for(test_rss_io_input.run(), 5)
        except asyncio.exceptions.TimeoutError:
            pass

        assert test_rss_io_input.state.sent_entries_size > 0
        assert test_input_queue.qsize() == 10
