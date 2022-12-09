from __future__ import annotations

import os.path
from typing import Generic, Optional, Type, TypeVar

from abc import ABC

import yaml

from mewbot.loader import load_component
from mewbot.core import Component
from mewbot.config import ConfigBlock


T_co = TypeVar("T_co", bound=Component, covariant=True)


class BaseTestClassWithConfig(ABC, Generic[T_co]):
    config_file: str
    implementation: Type[T_co]
    _config: Optional[ConfigBlock] = None
    _component: Optional[T_co] = None

    @property
    def config(self) -> ConfigBlock:
        """Returns the YAML-defined config the"""

        if not self._config:
            impl = self.implementation.__module__ + "." + self.implementation.__name__

            with open(self.config_file, "r", encoding="utf-8") as config:
                self._config = next(
                    document
                    for document in yaml.load_all(config, Loader=yaml.CSafeLoader)
                    if document["implementation"] == impl
                )

        return self._config

    @property
    def component(self) -> T_co:
        """Returns the component loaded from the config block"""

        if not self._component:
            component = load_component(self.config)
            assert isinstance(component, self.implementation), "Config loaded incorrect type"
            self._component = component

        return self._component

    @staticmethod
    def get_example_path(example_name: str, file_path: str = "", folder_prefix: str = "") -> str:
        """
        Returns the absolute path to a named example
        :param example_name: The name of the example to fetch the path for.
        :param file_path: The path to the file the test is running from
                          (allows you to override and look for examples elsewhere)
        :param folder_prefix: A prefix for the examples folder (e.g. "reddit_")
        :return:
        """
        # Is this elegant? No. Can it be improved? It SHOULD be.
        # Should be integrated with the plugin system to allow for easier examples request
        current_path = os.path.split(__file__)[0] if not file_path else os.path.split(file_path)[0]
        pkg_base_path = os.path.split(current_path)[0]

        examples_folder = os.path.join(pkg_base_path, folder_prefix + "examples")
        assert os.path.exists(examples_folder), f"examples folder {examples_folder} not found"

        example_path = os.path.join(examples_folder, example_name)
        assert os.path.isfile(
            example_path
        ), f"example folder {examples_folder} found, but no example {example_name} found therein"

        return example_path
