#!/use/bin/env python3

"""
The plugin manager is responsible for discovering mewbot plugins and loading them onto the
system.
"""

from mewbot.api.v1 import Behaviour, Action, Condition, Trigger
from mewbot.plugins.manager import PluginManager


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
    def test_get_plugins_output() -> None:
        """
        Tests that the plugin manager can provide metadata and plugins which it has loaded.
        :return:
        """

        test_manager = PluginManager()
        assert test_manager is not None

        assert "discord_dice_roller" in test_manager.get_available_plugin_names()

    @staticmethod
    def test_get_plugin_io_config_classes() -> None:
        """
        Tests the PluginManager's get_available_io_config_classes method.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        # There should now be one IOConfig class - the reddit one currently being used for
        # testing
        io_config_classes = test_manager.get_all_plugin_io_config_classes()
        assert isinstance(io_config_classes, tuple)

        assert len(io_config_classes) == 1

        io_config_classified_classes = test_manager.get_classified_io_config_classes()
        assert "reddit" in io_config_classified_classes.keys()

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
    def test_get_plugin_output_classes() -> None:
        """
        Tests the PluginManager's get_plugin_input_classes method.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        # At the moment there should be no Output presenting classes
        assert isinstance(test_manager.get_all_plugin_output_classes(), tuple)

        classified_output_classes = test_manager.get_classified_output_classes()
        assert not classified_output_classes

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

        assert [k for k in classified_triggers.keys()] == ["discord_dice_roller"], str(
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
    def test_plugin_manager_get_condition() -> None:
        """
        Tests that we can get a specific condition by name.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        dice_roller_behavior = test_manager.get_condition("MondayCondition")
        assert issubclass(dice_roller_behavior, Condition)

        # Try getting a behavior which does not, in fact, exist
        try:
            test_manager.get_condition("NotARealBehaviorBehaviorCondition")
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
