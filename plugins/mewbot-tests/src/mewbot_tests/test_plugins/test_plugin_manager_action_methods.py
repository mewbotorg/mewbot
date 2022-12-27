#!/use/bin/env python3

"""
The plugin manager is responsible for discovering mewbot plugins and loading them onto the
system.
"""

from mewbot.plugins.manager import PluginManager


class TestMewbotPluginManagerActionMethods:
    """
    Tests the mewbot plugin manager for action methods.
    """

    @staticmethod
    def test_get_plugin_action_classes() -> None:
        """
        Test the PluginManager's get_plugin_condition_classes method.
        Returns a tuple of all the Condition plugins known to the system.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        # There shouldn't be any Condition classes - for now
        plugin_action_classes = test_manager.get_all_plugin_action_classes()
        assert isinstance(plugin_action_classes, tuple)

        # There should be at least one from mewbot-discord_dice_roller
        assert len(plugin_action_classes) > 0

    @staticmethod
    def test_get_classified_action_classes() -> None:
        """
        Tests the get_classified_action_classes method.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        classified_action_classes = test_manager.get_classified_action_classes()
        assert isinstance(classified_action_classes, dict)

        assert "discord_dice_roller" in classified_action_classes.keys()
