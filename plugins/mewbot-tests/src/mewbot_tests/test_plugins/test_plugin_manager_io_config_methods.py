#!/use/bin/env python3

"""
The plugin manager is responsible for discovering mewbot plugins and loading them onto the
system.
"""

from mewbot.api.v1 import IOConfig
from mewbot.plugins.manager import PluginManager


class TestMewbotPluginManagerIOConfigMethods:
    """
    Tests the mewbot plugin manager - io config methods.
    """

    # ----------------------------------------------
    #
    # - IO CONFIGS

    @staticmethod
    def test_get_classified_io_config_classes() -> None:
        """
        Tests the manager get_classified_io_config_classes method
        Which should return the classified IOConfigs as a dict.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        # Check that the expected return is a dict
        classified_io_configs = test_manager.get_classified_io_config_classes()
        assert isinstance(classified_io_configs, dict)

        # Check that the returned dictionary has the right form
        # - keyed with, at least, reddit and valued with a tuple
        assert isinstance(classified_io_configs["reddit"], tuple)

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
    def test_plugin_manager_get_io_config_method() -> None:
        """
        Tests the PluginManager get_io_config method.
        :return:
        """
        test_manager = PluginManager()
        assert test_manager is not None

        mth_rtn = test_manager.get_io_config("RedditPasswordIO")
        assert issubclass(mth_rtn, IOConfig)

    #
    #
    # ----------------------------------------------
