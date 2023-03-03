# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

# Loads a file in, sees if it works

from __future__ import annotations

from typing import Type

from mewbot.test import BaseTestClassWithConfig

from mewbot.io.discord import DiscordIO
from mewbot.api.v1 import IOConfig

# pylint: disable=R0903
#  Disable "too few public methods" for test cases - most test files will be classes used for
#  grouping and then individual tests alongside these


class TestIoHttpsPost(BaseTestClassWithConfig[DiscordIO]):
    config_file: str = "examples/discord_bots/trivial_discord_bot.yaml"
    implementation: Type[DiscordIO] = DiscordIO

    def test_check_class(self) -> None:
        assert isinstance(self.component, DiscordIO)
        assert isinstance(self.component, IOConfig)
