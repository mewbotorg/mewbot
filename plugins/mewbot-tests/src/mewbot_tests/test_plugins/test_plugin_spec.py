#!/use/bin/env python3

"""
The plugin spec also supports some additional methods and properties that need to be tested
"""

import os

from typing import Tuple

from mewbot.plugins.hook_specs import (
    MewbotDevPluginSpec,
    gather_dev_paths,
    mewbot_dev_hook_impl,
)


class TestHookSpec:
    """
    Tests validation and check methods of the plugin spec.
    """

    @staticmethod
    def test_mewbot_dev_plugin_spec_validate_function_name() -> None:
        """
        Checks the validate_function_name method runs without throwing an error.
        :return:
        """
        assert MewbotDevPluginSpec.validate_function_name("declare_test_locs")

    @staticmethod
    def test_gather_dev_paths_with_declare_test_locs() -> None:
        """
        Tests the gather_dev_paths method with the function call declare_test_locs
        :return:
        """
        test_paths = gather_dev_paths(target_func="declare_test_locs")

        for path in test_paths:
            assert isinstance(path, str)
            assert os.path.exists(path)

    @staticmethod
    def test_gather_dev_paths_with_declare_test_locs_add_invalid_path() -> None:
        """
        Tests the gather_dev_paths method with the function call declare_test_locs
        :return:
        """
        # We are declaring a known bad path to trip some of the checks
        @mewbot_dev_hook_impl  # type: ignore
        def declare_test_locs() -> Tuple[Tuple[str, ...], ...]:
            """
            If we declare the location of this plugin's tests then they can be included in the main
            test run.
            :return:
            """
            return tuple(
                [
                    tuple(["Not", "Valid"]),
                ]
            )

        test_paths = gather_dev_paths(target_func="declare_test_locs")

        for path in test_paths:
            assert isinstance(path, str)
            assert os.path.exists(path)
