#!/use/bin/env python3

"""
The plugin manager is responsible for discovering mewbot plugins and loading them onto the
system.
"""

from mewbot.api.v1 import Behaviour, Action, Condition, Trigger, IOConfig
from mewbot.plugins.manager import PluginManager


class TestMewbotPluginManagerBehaviorMethods:
    """
    Tests the mewbot plugin manager.
    """
    @staticmethod
    def test_get_plugin_behavior_classes() -> None:
        """
        Test the PluginManager's get_plugin_condition_classes method.
        Returns a tuple of all the Condition plugins known to the system.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        # There shouldn't be any Condition classes - for now
        plugin_behavior_classes = test_manager.get_all_plugin_behavior_classes()
        assert isinstance(plugin_behavior_classes, tuple)

        # There should be at least one from mewbot-discord_dice_roller
        assert len(plugin_behavior_classes) > 0

    @staticmethod
    def test_get_classified_behavior_classes() -> None:
        """
        Tests the PluginManager's get_classified_behavior_classes method.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        classified_behavior_plugins = test_manager.get_classified_behavior_classes()

        assert isinstance(classified_behavior_plugins, dict)
        assert isinstance(classified_behavior_plugins["discord_dice_roller"], tuple)

    @staticmethod
    def test_plugin_manager_get_behavior() -> None:
        """
        Returns a specific behavior by name.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        dice_roller_behavior = test_manager.get_behavior("DiscordDiceRollerBehavior")
        assert issubclass(dice_roller_behavior, Behaviour)

        # Try getting a behavior which does not, in fact, exist
        try:
            test_manager.get_behavior("NotARealBehaviorBehavior")
        except ModuleNotFoundError:
            pass
