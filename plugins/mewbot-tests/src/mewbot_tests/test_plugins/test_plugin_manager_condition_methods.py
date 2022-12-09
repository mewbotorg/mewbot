#!/use/bin/env python3

"""
The plugin manager is responsible for discovering mewbot plugins and loading them onto the
system.
"""

from mewbot.api.v1 import Condition
from mewbot.plugins.manager import PluginManager



class TestMewbotPluginManagerConditionMethods:
    """
    Tests the mewbot plugin manager.
    """

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
    def test_get_classified_condition_classes_method() -> None:
        """
        Tests the get_classified_condition_classes method.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        classified_con_classes = test_manager.get_classified_condition_classes()
        assert isinstance(classified_con_classes, dict)

        assert "extended_conditions" in classified_con_classes.keys()


