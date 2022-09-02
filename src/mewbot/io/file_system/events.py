from typing import Union, Optional

import dataclasses

import aiopath  # type: ignore
import watchfiles
from watchdog.events import FileSystemEvent  # type: ignore

from mewbot.api.v1 import InputEvent


@dataclasses.dataclass
class FileSystemInputEvent(InputEvent):
    """
    Base class for generic input events generated by the file system.
    """

    # equivalent to FileSystemEvent, tuple[watchfiles.Change, str], None]
    base_event: Optional[Union[FileSystemEvent, tuple[watchfiles.Change, str]]]


#
# --------------------------------------
# - INPUT - FILE TYPE
# --------------------------------------
#

@dataclasses.dataclass
class FileMonitorInputEvent(FileSystemInputEvent):
    """
    Base class for file related input events generated by the file system.
    """

    file: aiopath.AsyncPath

    @property
    def path(self) -> str:
        return str(self.file)


@dataclasses.dataclass
class MonitoredFileWasCreatedInputEvent(FileMonitorInputEvent):
    """
    Called when a file is created - either at the location which is being monitored or inside a dir
    which is being monitored.
    """


@dataclasses.dataclass
class MonitoredFileWasUpdatedInputEvent(FileMonitorInputEvent):
    """
    Called when a file is updated - either at the location which is being monitored or inside a dir
    which is being monitored.
    """


@dataclasses.dataclass
class FileMovedIntoOrFromWatchedDirInputEvent(FileMonitorInputEvent):
    """
    Called when a file is updated - either at the location which is being monitored or inside a dir
    which is being monitored.
    """

    file_src: str


@dataclasses.dataclass
class MonitoredFileWasDeletedInputEvent(FileMonitorInputEvent):
    """
    Called when a file is created - either at the location which is being monitored or inside a dir
    which is being monitored.
    Cannot provide any more information without caching a lot of details about the FS.
    """


@dataclasses.dataclass
class WatchedFileWasDeletedOrMovedInputEvent(FileMonitorInputEvent):
    """
    Event called when a file is removed from the monitored location - the input location.
    Note - the input cannot distinguish between a file being deleted or moved away from the input
    location.
    """


#
# --------------------------------------
# - INPUT - DIR TYPE
# --------------------------------------
#


@dataclasses.dataclass
class DirectoryMonitorInputEvent(FileSystemInputEvent):
    """
    Base class for file related input events generated by the file system.
    """

    dir: aiopath.AsyncPath

    @property
    def path(self) -> str:
        return str(self.dir)


@dataclasses.dataclass
class DirectoryCreatedInWatchedDirInputEvent(DirectoryMonitorInputEvent):
    """
    A dir has been created - either the dir we're monitoring - if we're monitoring one.
    Or at the given monitor location.
    """


@dataclasses.dataclass
class DirectoryInMonitoredDirectoryWasUpdatedInputEvent(DirectoryMonitorInputEvent):
    """
    A dir has been updated - either in the dir we're monitoring - if we're monitoring one.
    What this mostly means is the name of the dir has been updated.
    If the contents have been updated, it'll spew events of the appropriate type.
    """


@dataclasses.dataclass
class DirectoryMovedIntoOrFromWatchedDirInputEvent(DirectoryMonitorInputEvent):
    """
    A dir has been updated - either in the dir we're monitoring - if we're monitoring one.
    What this mostly means is the name of the dir has been updated.
    If the contents have been updated, it'll spew events of the appropriate type.
    """

    dir_moved_from: aiopath.AsyncPath

    @property
    def moved_from_path(self) -> str:
        return str(self.dir_moved_from)


@dataclasses.dataclass
class DirectoryDeletedInMonitoredDirectoryInputEvent(DirectoryMonitorInputEvent):
    """
    A dir has been deleted - either in the dir we're monitoring - if we're monitoring one.
    """


class FileCreatedInMonitoredDirectoryInputEvent(FileMonitorInputEvent, DirectoryMonitorInputEvent):
    """
    Event called when a dir comes into existence at the monitored location - the input location.
    Note - the input cannot distinguish between a dir being created or moved to the input location.
    """

    def __init__(
        self, monitored_directory: aiopath.AsyncPath, created_path: aiopath.AsyncPath
    ) -> None:
        super(FileMonitorInputEvent, self).__init__(file=created_path)
        super(DirectoryMonitorInputEvent, self).__init__(dir=monitored_directory)

    @property
    def directory(self) -> str:
        return str(self.dir)

    @property
    def path(self) -> str:
        return str(self.file)


@dataclasses.dataclass
class FileDeletedFromMonitoredDirectoryInputEvent(FileMonitorInputEvent, DirectoryMonitorInputEvent):
    """
    Event called when a dir is removed from the monitored location - the input location.
    Note - the input cannot distinguish between a dir being deleted or moved away from the input
    location.
    """

    def __init__(
        self, monitored_directory: aiopath.AsyncPath, deleted_path: aiopath.AsyncPath
    ) -> None:
        super(FileMonitorInputEvent, self).__init__(file=deleted_path)
        super(DirectoryMonitorInputEvent, self).__init__(dir=monitored_directory)

    @property
    def directory(self) -> str:
        return str(self.dir)

    @property
    def path(self) -> str:
        return str(self.file)
