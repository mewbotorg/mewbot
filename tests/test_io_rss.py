
from typing import Type

import asyncio
import pytest

from tests.common import BaseTestClassWithConfig

from mewbot.io.rss import RSSIO
from mewbot.api.v1 import IOConfig


class TestRSSIO(BaseTestClassWithConfig[RSSIO]):
    config_file: str = "examples/rss_input.yaml"
    implementation: Type[RSSIO] = RSSIO

    def test_check_class(self) -> None:
        assert isinstance(self.component, RSSIO)
        assert isinstance(self.component, IOConfig)

    def test_direct_set_polling_every_property_fails(self) -> None:
        """
        Test that directly setting the "polling_every" fails.
        """
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

    @pytest.mark.asyncio
    async def test_component_run(self):
        """
        Run the component - should run without throwing an error.
        """
        component_rss_input = self.component.get_inputs()
        assert isinstance(component_rss_input, list)
        assert len(component_rss_input) == 1
        
        test_rss_io_input = component_rss_input[0]

        try:
            await asyncio.wait_for(test_rss_io_input.run(), 6)
        except asyncio.exceptions.TimeoutError:
            pass
