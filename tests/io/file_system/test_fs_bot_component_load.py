from __future__ import annotations

from typing import Type

from tests.common import BaseTestClassWithConfig

from mewbot.io.file_system import FileSystemMonitor
from mewbot.api.v1 import IOConfig

# pylint: disable=R0903
#  Disable "too few public methods" for test cases - most test files will be classes used for
#  grouping and then individual tests alongside these


class TestIoFileSystem(BaseTestClassWithConfig[FileSystemMonitor]):
    config_file: str = "examples/file_system_bots/file_input_monitor_bot.yaml"
    implementation: Type[FileSystemMonitor] = FileSystemMonitor

    def test_check_class(self) -> None:
        assert isinstance(self.component, FileSystemMonitor)
        assert isinstance(self.component, IOConfig)
