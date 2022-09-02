#!/usr/bin/env python3

from __future__ import annotations

from typing import Optional, Sequence, Union

from mewbot.api.v1 import IOConfig, Input, Output
from mewbot.io.file_system.events import (
    FileSystemInputEvent,
    FileMonitorInputEvent,
    MonitoredFileWasCreatedInputEvent,
    MonitoredFileWasUpdatedInputEvent,
    FileMovedIntoOrFromWatchedDirInputEvent,
    MonitoredFileWasDeletedInputEvent,
    MonitoredFileWasCreatedInputEvent,
    WatchedFileWasDeletedOrMovedInputEvent,
    DirectoryCreatedInWatchedDirInputEvent,
    DirectoryInMonitoredDirectoryWasUpdatedInputEvent,
    DirectoryMovedIntoOrFromWatchedDirInputEvent,
    DirectoryDeletedInMonitoredDirectoryInputEvent,
    FileCreatedInMonitoredDirectoryInputEvent,
    FileDeletedFromMonitoredDirectoryInputEvent,
)
from mewbot.io.file_system.inputs import FileTypeFSInput, DirTypeFSInput

__all__ = (
    "FileSystemInputEvent",
    "FileMonitorInputEvent",
    "MonitoredFileWasCreatedInputEvent",
    "MonitoredFileWasUpdatedInputEvent",
    "FileMovedIntoOrFromWatchedDirInputEvent",
    "MonitoredFileWasDeletedInputEvent",
    "MonitoredFileWasCreatedInputEvent",
    "WatchedFileWasDeletedOrMovedInputEvent",
    "DirectoryCreatedInWatchedDirInputEvent",
    "DirectoryInMonitoredDirectoryWasUpdatedInputEvent",
    "DirectoryMovedIntoOrFromWatchedDirInputEvent",
    "DirectoryDeletedInMonitoredDirectoryInputEvent",
    "FileCreatedInMonitoredDirectoryInputEvent",
    "FileDeletedFromMonitoredDirectoryInputEvent",
    "FileTypeFSInput",
    "DirTypeFSInput",
)


class FileSystemIO(IOConfig):

    _input: Optional[Union[FileTypeFSInput, DirTypeFSInput]] = None

    _input_path: Optional[str] = None
    _input_path_type: str = "not_set"

    @property
    def input_path(self) -> Optional[str]:
        return self._input_path

    @input_path.setter
    def input_path(self, input_path: str) -> None:
        self._input_path = input_path

    @property
    def input_path_type(self) -> str:
        """
        When starting this class you need to set the type of resource you are monitoring.
        This is due to limitations of the underlying libraries used to do the actual monitoring.
        """
        return self._input_path_type

    @input_path_type.setter
    def input_path_type(self, input_path_type: str) -> None:
        assert input_path_type in (
            "dir",
            "file",
        ), f"input_path_type couldn't be set as {input_path_type}"
        self._input_path_type = input_path_type

    def get_inputs(self) -> Sequence[Input]:
        assert self._input_path_type in ("dir", "file",), (
            f"input_path_type must be properly set before startup - "
            f"{self._input_path_type} is not proper"
        )

        if not self._input:

            if self._input_path_type == "file":
                self._input = FileTypeFSInput(self._input_path)
            elif self._input_path_type == "dir":
                self._input = DirTypeFSInput(self._input_path)
            else:
                raise NotImplementedError(
                    f"{self._input_path_type} not good. Options are 'dir' and 'file'"
                )

        return [self._input]

    def get_outputs(self) -> Sequence[Output]:
        return []
