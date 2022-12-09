#!/use/bin/env python3

"""
The plugin manager is responsible for discovering mewbot plugins and loading them onto the
system.
"""

from mewbot.api.v1 import Behaviour, Action, Condition, Trigger, IOConfig
from mewbot.plugins.manager import PluginManager


class TestMewbotPluginManagerInputMethods:
    """
    Tests the mewbot plugin manager.
    """
    @staticmethod
    def test_get_plugin_input_classes() -> None:
        """
        Tests the PluginManager's get_plugin_input_classes method.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        # There should now be some reddit input presenting classes
        assert isinstance(test_manager.get_all_plugin_input_classes(), tuple)

        classified_input_classes = test_manager.get_classified_input_classes()
        assert "reddit" in classified_input_classes.keys()

    @staticmethod
    def test_get_classified_input_classes() -> None:
        """
        Tests the PluginManager's get_classified_input_classes method.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        classified_inputs = test_manager.get_classified_input_classes()
        assert isinstance(classified_inputs, dict)

        assert "reddit" in classified_inputs.keys()
        assert isinstance(classified_inputs["reddit"], tuple)


