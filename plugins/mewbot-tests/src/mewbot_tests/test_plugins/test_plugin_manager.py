#!/use/bin/env python3

"""
The plugin manager is responsible for discovering mewbot plugins and loading them onto the
system.
"""

from typing import Dict, Type, Tuple

from mewbot.api.v1 import Action, Condition, Trigger
from mewbot.plugins.manager import PluginManager
from mewbot.plugins.hook_specs import mewbot_ext_hook_impl


class TestMewbotPluginManager:
    """
    Tests the mewbot plugin manager.
    """

    @staticmethod
    def test_plugin_manager_init() -> None:
        """
        Tests that the PluginManager will initialize.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

    @staticmethod
    def test_get_plugin_trigger_classes() -> None:
        """
        Test the PluginManager's get_plugin_trigger_classes method.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        # At the moment there should be at least one Trigger presenting class
        plugin_trigger_classes = test_manager.get_all_plugin_trigger_classes()
        assert isinstance(plugin_trigger_classes, tuple)

        # Hopefully a number of plugins should have been imported - or this test should not
        # be run
        assert len(plugin_trigger_classes) > 0

        classified_triggers = test_manager.get_classified_trigger_classes()

        assert list(classified_triggers.keys()) == ["discord_dice_roller"], str(
            classified_triggers.keys()
        )

    @staticmethod
    def test_get_plugin_trigger_classes_including_bad_trigger() -> None:
        """
        Test the PluginManager's get_plugin_trigger_classes method.
        :return:
        """
        @mewbot_ext_hook_impl  # type: ignore
        def get_trigger_classes() -> Dict[str, Tuple[Type[Tuple[str, ...]], ...]]:
            """
            Return the trigger classes defined in this plugin.
            :return:
            """
            return {
                "bd_trigger": tuple(
                    [tuple, ]
                )
            }

        test_manager = PluginManager()
        assert test_manager is not None

        # At the moment there should be at least one Trigger presenting class
        plugin_trigger_classes = test_manager.get_all_plugin_trigger_classes()
        assert isinstance(plugin_trigger_classes, tuple)

        # Hopefully a number of plugins should have been imported - or this test should not
        # be run
        assert len(plugin_trigger_classes) > 0

        classified_triggers = test_manager.get_classified_trigger_classes()

        assert list(classified_triggers.keys()) == ["discord_dice_roller"], str(
            classified_triggers.keys()
        )


    @staticmethod
    def test_get_plugin_condition_classes() -> None:
        """
        Test the PluginManager's get_plugin_condition_classes method.
        Returns a tuple of all the Condition plugins known to the system.
        Todo: System should complain if an trigger which cannot be triggered is added to the system
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        # There shouldn't be any Condition classes - for now
        plugin_condition_classes = test_manager.get_all_plugin_condition_classes()
        assert isinstance(plugin_condition_classes, tuple)



    @staticmethod
    def test_get_available_plugin_classes() -> None:
        """
        Tests the get_available_plugin_classes method
        Which should return a dictionary keyed with the plugin value and valued
        with the names of the available plugins of that type.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        call_result = test_manager.get_all_available_plugin_class_names()

        assert isinstance(call_result, dict)

        # Plugin which should have been picked up from mewbot-discord_dice_roller
        assert "DiscordDiceRollerBehavior" in call_result["Behaviors"]
        assert "MondayCondition" in call_result["Conditions"]
        assert "NotMondayCondition" in call_result["Conditions"]
        assert "DiscordDiceRollCommandTrigger" in call_result["Triggers"]
        assert "RedditOutput" in call_result["Outputs"]

    @staticmethod
    def test_get_available_plugin_classes_with_bad_class() -> None:
        """
        Tests the get_available_plugin_classes method
        Which should return a dictionary keyed with the plugin value and valued
        with the names of the available plugins of that type.
        :return:
        """
        @mewbot_ext_hook_impl  # type: ignore
        def get_io_config_classes() -> Dict[str, Tuple[Type[Tuple], ...]]:
            """
            Return the IOConfigs defined by this plugin module.
            Note - IOConfig needs to be extended with YAML signature info - though this can also
            be generated from properties.
            :return:
            """
            return {
                "bad_plugin": tuple(
                    [
                        Tuple,
                    ]
                )
            }

        test_manager = PluginManager()
        assert test_manager is not None

        call_result = test_manager.get_all_available_plugin_class_names()

        assert isinstance(call_result, dict)

        # Plugin which should have been picked up from mewbot-discord_dice_roller
        assert "DiscordDiceRollerBehavior" in call_result["Behaviors"]
        assert "MondayCondition" in call_result["Conditions"]
        assert "NotMondayCondition" in call_result["Conditions"]
        assert "DiscordDiceRollCommandTrigger" in call_result["Triggers"]
        assert "RedditOutput" in call_result["Outputs"]

    @staticmethod
    def test_plugin_manager_get_action() -> None:
        """
        Tests the return of a specific action by name.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        dice_roller_behavior = test_manager.get_action("DiscordRollTextResponse")
        assert issubclass(dice_roller_behavior, Action)

        # Try getting a behavior which does not, in fact, exist
        try:
            test_manager.get_action("NotARealBehaviorAction")
        except ModuleNotFoundError:
            pass

    @staticmethod
    def test_plugin_manager_get_trigger() -> None:
        """
        Tests that we can get a specific trigger by name.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        dice_roller_trigger = test_manager.get_trigger("DiscordDiceRollCommandTrigger")
        assert issubclass(dice_roller_trigger, Trigger)

        # Try getting a behavior which does not, in fact, exist
        try:
            test_manager.get_trigger("NotARealBehaviorBehaviorCondition")
        except ModuleNotFoundError:
            pass
