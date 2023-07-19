from __future__ import annotations

from typing import Type

from mewbot.test import BaseTestClassWithConfig

from mewbot.io.file_system_monitor import FileSystemMonitorIO
from mewbot.api.v1 import IOConfig

# pylint: disable=R0903
#  Disable "too few public methods" for test cases - most test files will be classes used for
#  grouping and then individual tests alongside these


class TestIoFileSystem(BaseTestClassWithConfig[FileSystemMonitorIO]):
    config_file: str = "examples/file_system_bots/file_input_monitor_bot.yaml"
    implementation: Type[FileSystemMonitorIO] = FileSystemMonitorIO

    def test_check_class(self) -> None:
        assert isinstance(self.component, FileSystemMonitorIO)
        assert isinstance(self.component, IOConfig)
