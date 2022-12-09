#!/use/bin/env python3

"""
The plugin manager is responsible for discovering mewbot plugins and loading them onto the
system.
"""

from mewbot.api.v1 import Behaviour, Action, Condition, Trigger, IOConfig, Output
from mewbot.plugins.manager import PluginManager



class TestMewbotPluginManagerOutputMethods:
    """
    Tests the mewbot plugin manager - specifically methods involved with retrieving inputs.
    """

    @staticmethod
    def test_get_plugins_output() -> None:
        """
        Tests that the plugin manager can provide metadata and plugins which it has loaded.
        :return:
        """

        test_manager = PluginManager()
        assert test_manager is not None

        assert "discord_dice_roller" in test_manager.get_available_plugin_names()

    @staticmethod
    def test_get_plugin_output_classes() -> None:
        """
        Tests the PluginManager's get_plugin_output_classes method.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        # At the moment there should be no Output presenting classes
        assert isinstance(test_manager.get_all_plugin_output_classes(), tuple)

        classified_output_classes = test_manager.get_classified_output_classes()
        assert "reddit" in classified_output_classes
        assert isinstance(classified_output_classes["reddit"], tuple)

    @staticmethod
    def test_get_plugin_output_class_from_name() -> None:
        """
        Tests the PluginManager's get_plugin_output_classes method.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        named_output = test_manager.get_output("RedditOutput")

        assert issubclass(named_output, Output)
