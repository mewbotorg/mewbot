# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Provides base objects for the file system monitoring subsystem.

Includes valid InputEvents for the file system monitor.
"""

from typing import Optional, Union

import dataclasses
from pathlib import Path

import watchfiles
from watchdog.events import FileSystemEvent  # type: ignore

from mewbot.api.v1 import InputEvent


@dataclasses.dataclass
class FSInputEvent(InputEvent):
    """
    Base class for generic input events generated by the file system.
    """

    # equivalent to FileSystemEvent, tuple[watchfiles.Change, str], None]
    base_event: Optional[Union[FileSystemEvent, tuple[watchfiles.Change, str]]]


#
# --------------------------------------
# - INPUT - WATCHING A LOCATION
# --------------------------------------
#

# - FILE AT LOCATION


@dataclasses.dataclass
class FileAtWatchLocInputEvent(FSInputEvent):
    """
    Base class for file related input events - generated when a file is being watched for changes.
    """

    path: str


@dataclasses.dataclass
class FileCreatedAtWatchLocationFSInputEvent(FileAtWatchLocInputEvent):
    """
    A file has been created on the system within a dir being monitored.
    """


@dataclasses.dataclass
class FileUpdatedAtWatchLocationFSInputEvent(FileAtWatchLocInputEvent):
    """
    A file has been updated at the location being watched.
    """


@dataclasses.dataclass
class FileDeletedFromWatchLocationFSInputEvent(FileAtWatchLocInputEvent):
    """
    A file has been deleted from the location being watched.
    """


# - DIR AT LOCATION


@dataclasses.dataclass
class DirAtWatchLocInputEvent(FSInputEvent):
    """
    Base class for file related input events - generated when a file is being watched for changes.
    """

    path: str


@dataclasses.dataclass
class DirCreatedAtWatchLocationFSInputEvent(DirAtWatchLocInputEvent):
    """
    A directory has been created on the system within a dir being monitored.
    """


@dataclasses.dataclass
class DirUpdatedAtWatchLocationFSInputEvent(DirAtWatchLocInputEvent):
    """
    A dir has been updated at the location being watched.
    """


@dataclasses.dataclass
class DirMovedToWatchLocationFSInputEvent(DirAtWatchLocInputEvent):
    """
    A dir has been moved to the location being watched.
    """

    file_src: str


@dataclasses.dataclass
class DirMovedFromWatchLocationFSInputEvent(DirAtWatchLocInputEvent):
    """
    A dir has been moved away from the location being watched.
    """

    file_src: str


@dataclasses.dataclass
class DirDeletedFromWatchLocationFSInputEvent(DirAtWatchLocInputEvent):
    """
    A dir has been deleted from the location being watched.
    """


# - WITHIN THE DIR AT LOCATION


@dataclasses.dataclass
class WithinDirAtWatchLocInputEvent(DirAtWatchLocInputEvent):
    """
    Base class for file related input events - generated when a file is being watched for changes.
    """

    path: str


@dataclasses.dataclass
class FileCreatedWithinWatchedDirFSInputEvent(WithinDirAtWatchLocInputEvent):
    """
    A file has been created on the system within a dir being monitored.
    """


@dataclasses.dataclass
class FileUpdatedWithinWatchedDirFSInputEvent(WithinDirAtWatchLocInputEvent):
    """
    A file has been updated at the location being watched.
    """


@dataclasses.dataclass
class FileMovedWithinWatchedDirFSInputEvent(WithinDirAtWatchLocInputEvent):
    """
    A file has been moved to the location being watched.
    """

    file_src: str
    file_dst: str


@dataclasses.dataclass
class FileMovedOutsideWatchedDirFSInputEvent(WithinDirAtWatchLocInputEvent):
    """
    A file has been moved to the location being watched.
    """

    file_src: str


@dataclasses.dataclass
class FileDeletedWithinWatchedDirFSInputEvent(WithinDirAtWatchLocInputEvent):
    """
    A file has been deleted from the location being watched.
    """


# - DIR AT LOCATION


@dataclasses.dataclass
class DirCreatedWithinWatchedDirFSInputEvent(WithinDirAtWatchLocInputEvent):
    """
    A directory has been created on the system within a dir being monitored.
    """


@dataclasses.dataclass
class DirUpdatedWithinWatchedDirFSInputEvent(WithinDirAtWatchLocInputEvent):
    """
    A dir has been updated at the location being watched.
    """


@dataclasses.dataclass
class DirMovedWithinWatchedDirFSInputEvent(WithinDirAtWatchLocInputEvent):
    """
    A dir has been moved to the location being watched.
    """

    dir_src_path: Union[str, Path]
    dir_dst_path: Union[str, Path]


@dataclasses.dataclass
class DirMovedOutOfWatchedDirFSInputEvent(WithinDirAtWatchLocInputEvent):
    """
    A dir has been moved to the location being watched.
    """

    dir_src_path: Union[str, Path]
    dir_dst_path: Union[str, Path]


@dataclasses.dataclass
class DirDeletedFromWatchedDirFSInputEvent(WithinDirAtWatchLocInputEvent):
    """
    A dir has been deleted from the location being watched.
    """
