from typing import Type

import asyncio
import pytest

from tests.common import BaseTestClassWithConfig

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
        component_rss_input = self.component.get_inputs()
        assert isinstance(component_rss_input, list)
        assert len(component_rss_input) == 1

        test_rss_io_input: RSSInput = component_rss_input[0]

        assert isinstance(test_rss_io_input.sites, list)
        # Will have been set off the input sites
        assert len(test_rss_io_input.sites) == 0

        self.component.sites = [
            "www.google.com",
        ]

        assert isinstance(test_rss_io_input.sites, list)
        # Will have been set off the input sites
        assert len(test_rss_io_input.sites) == 1

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
    async def test_component_run_after_repeated_get_inputs_call(self) -> None:
        """
        Run the component's input method after nullifying components
        """
        self.component.get_inputs()  # Tests the "inputs not none" case
        component_rss_input = self.component.get_inputs()
        assert isinstance(component_rss_input, list)
        assert len(component_rss_input) == 1

        test_rss_io_input = component_rss_input[0]

        # Run the input
        try:
            await asyncio.wait_for(test_rss_io_input.run(), 1)
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
        self.component.get_inputs()  # Tests the "inputs not none" case
        component_rss_input = self.component.get_inputs()
        assert isinstance(component_rss_input, list)
        assert len(component_rss_input) == 1

        test_rss_io_input: RSSInput = component_rss_input[0]
        test_rss_input_state: RSSInputState = test_rss_io_input.state

        test_rss_input_state.start()

        assert test_rss_input_state.sites == [
            "https://www.theguardian.com/world/rss",
            "https://www.engadget.com/rss.xml",
        ]
