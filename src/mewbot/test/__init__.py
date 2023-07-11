#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Provides support classes and objects for mewbot tests.
"""

from __future__ import annotations

from typing import Generic, Optional, Type, TypeVar

from abc import ABC

import yaml

from mewbot.core import Component, ConfigBlock
from mewbot.loader import load_component

T_co = TypeVar("T_co", bound=Component, covariant=True)


class BaseTestClassWithConfig(ABC, Generic[T_co]):
    """
    Base for a class of tests designed to test components in isolation.

    Class offers the features of
     - loads a configuration from a config file
     - isolates a particular component from within that config file
     - (determined by overriding implementation with the class type you want to examine)
     - presents that component, along with the yaml which defines it, for testing
    """

    config_file: str
    implementation: Type[T_co]
    _config: Optional[ConfigBlock] = None
    _component: Optional[T_co] = None

    @property
    def config(self) -> ConfigBlock:
        """Returns the YAML-defined config for the given implementation."""

        if not self._config:
            impl = self.implementation.__module__ + "." + self.implementation.__name__

            with open(self.config_file, "r", encoding="utf-8") as config:
                _docs = [
                    document
                    for document in yaml.load_all(config, Loader=yaml.CSafeLoader)
                    if document["implementation"] == impl
                ]
                self._config = _docs[0]

        return self._config

    @property
    def component(self) -> T_co:
        """Returns the component loaded from the config block."""

        if not self._component:
            component = load_component(self.config)
            assert isinstance(component, self.implementation), "Config loaded incorrect type"
            self._component = component

        return self._component
