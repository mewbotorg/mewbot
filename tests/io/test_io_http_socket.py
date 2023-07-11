# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Unified test of http and socket parts of mewbot.io.

Loads a file in, sees if it works, and then probes the socket and http class.
"""

from __future__ import annotations

from typing import Type

import copy

from mewbot.api.v1 import IOConfig
from mewbot.io.http import HTTPServlet
from mewbot.io.socket import SocketIO
from mewbot.test import BaseTestClassWithConfig

# pylint: disable=R0903
#  Disable "too few public methods" for test cases - most test files will be classes used for
#  grouping and then individual tests alongside these


class TestIoHttpsPost(BaseTestClassWithConfig[HTTPServlet]):
    """
    Unified test of http and socket parts of mewbot.io.

    Loads a file in, sees if it works, and then probes the socket and http class.
    """

    config_file: str = "examples/trivial_http_post.yaml"
    implementation: Type[HTTPServlet] = HTTPServlet

    def test_check_class(self) -> None:
        """Test instance creation."""

        assert isinstance(self.component, HTTPServlet)
        assert isinstance(self.component, SocketIO)
        assert isinstance(self.component, IOConfig)

    def test_check_setget(self) -> None:
        """Test property get/set."""

        temp_component = copy.deepcopy(self.component)

        new_host = "nullfailtouse"
        temp_component.host = new_host
        assert temp_component.host == new_host

        new_port = 0
        temp_component.port = new_port
        assert temp_component.port == new_port
