#!/usr/bin/env python3

from __future__ import annotations

from typing import AsyncGenerator, Dict, Optional, Set, Type

import asyncio
import logging

import watchfiles
from watchfiles.main import FileChange
from aiopath.path import AsyncPath

from mewbot.api.v1 import Input
from mewbot.core import InputEvent

from .base import FileSystemInputEvent


class FileMonitorInputEvent(FileSystemInputEvent):
    """
    Base class for file related input events generated by the file system.
    """

    file: AsyncPath

    def __init__(self, file: AsyncPath) -> None:
        self.file = file

    @property
    def path(self) -> str:
        return str(self.file)


class MonitoredFileWasCreatedInputEvent(FileMonitorInputEvent):
    """
    Called when a file is created - either at the location which is being monitored or inside a dir
    which is being monitored.
    """


class MonitoredFileWasUpdatedInputEvent(FileMonitorInputEvent):
    """
    Called when a file is updated - either at the location which is being monitored or inside a dir
    which is being monitored.
    """


class MonitoredFileWasDeletedOrMovedInputEvent(FileMonitorInputEvent):
    """
    Event called when a file is removed from the monitored location - the input location.
    Note - the input cannot distinguish between a file being deleted or moved away from the input
    location.
    """


class FileMonitorInput(Input):
    """
    Using watchfiles as a backend to watch for events from a single file.
    Augmented by checks so that the system responds properly if the file does not initially exist.
    Or is deleted during the monitoring process.
    If the watcher is started on a folder, it will wait for the folder to go away before starting.
    If the file is deleted and replaced with a folder, it will wait for the folder to be replaced
    with a file before monitoring.
    """

    @staticmethod
    def produces_inputs() -> Set[Type[InputEvent]]:
        """
        Defines the set of input events this Input class can produce.
        This type of InputClass monitors a single file
        So a number of the file type inputs make no sense for it.
        """
        return {
            MonitoredFileWasCreatedInputEvent,  # A file is created at the monitored point
            MonitoredFileWasUpdatedInputEvent,  # The monitored file is updated
            MonitoredFileWasDeletedOrMovedInputEvent,  # The monitored file is deleted
        }

    _logger: logging.Logger

    _monitored_path: Optional[AsyncPath]  # A location on the file system to monitor
    _path_change_event: Optional[asyncio.Event]  # Event to trigger if path is updated

    _run = False
    _polling_interval: float = 0.5

    def __init__(self, path: Optional[AsyncPath] = None) -> None:
        super().__init__()

        self._logger = logging.getLogger(__name__ + ":" + type(self).__name__)
        self._monitored_path = None
        self._path_change_event = None
        self._run = False

        if path:
            self.input_path = path

    @property
    def input_path(self) -> Optional[str]:
        return str(self._monitored_path) if self._monitored_path else None

    @input_path.setter
    def input_path(self, new_input_path: Optional[str]) -> None:
        self._monitored_path = AsyncPath(new_input_path)
        if self._path_change_event:
            self._path_change_event.set()

    async def run(self) -> None:
        self._path_change_event = asyncio.Event()
        self._run = True

        self._logger.info("Starting File Monitor")
        while self._run:
            watcher = await self._acquire_watcher()

            if watcher is None:
                self._logger.info("Watcher not acquired (target file changed or shutting down?)")
                continue

            async for event in self._monitor_file_watcher(watcher):
                self._logger.debug("Sending event %s", event)
                await self.queue.put(event)

        self._logger.info("FileMonitorInput exiting run loop")

    async def shutdown(self) -> None:
        self._logger.info("Requesting shutdown of FileMonitor")
        self._run = False
        if self._path_change_event is not None:
            self._logger.debug("Triggering cancel event")
            self._path_change_event.set()

    async def _acquire_watcher(self) -> Optional[AsyncGenerator[Set[FileChange], None]]:
        if not self._path_change_event:
            self._path_change_event = asyncio.Event()

        while not self._monitored_path:
            self._logger.info("No path selected, waiting for one to be set")
            await self._path_change_event.wait()
            self._path_change_event = asyncio.Event()

        path = self._monitored_path
        self._logger.info("Starting up file monitor, current path is %s", path)

        if not await path.is_file():
            self._logger.info("Path %s not a regular file, waiting...", path)
            ready = await self._wait_for_path_to_be_regular_file(path)

            # Waiting exited before the file exists due to the event flag being set.
            if not ready:
                return None

            # FIXME: Need to throw the creation event
        else:
            self._logger.info("Path %s already exists as a regular file", path)

        return watchfiles.awatch(path, stop_event=self._path_change_event)

    async def _wait_for_path_to_be_regular_file(self, path: AsyncPath) -> bool:
        """
        Preforms a check on the file - updating if needed.
        """
        if not self._path_change_event:
            self._path_change_event = asyncio.Event()

        while self._run and not self._path_change_event.is_set():
            self._logger.debug("Checking for %s", path)
            exists = await path.exists()
            is_file = await path.is_file()

            # If the file doesn't currently exist, wait until it turns up
            if exists and is_file:
                self._logger.debug("File has become available")
                return True

            self._logger.debug("Path is not a regular: exists=%s, is_file=%s", exists, is_file)
            await asyncio.sleep(self._polling_interval)

        self._logger.info("Abandoning watcher acquisition %s", "Requested path changed" if self._run else "Input shutting down")
        return False

    async def _monitor_file_watcher(
        self, watcher: AsyncGenerator[Set[FileChange], None]
    ) -> AsyncGenerator[FileMonitorInputEvent, None]:
        """
        Actually do the job of monitoring and responding to the watcher.
        If the file is detected as deleted, then the
        """
        self._logger.info("Reading events for existing regular file %s", self._monitored_path)

        if not self._path_change_event:
            self._path_change_event = asyncio.Event()

        async for changes in watcher:
            # Changes are sets of chance objects
            # tuples with
            #  - the first entry being a watchfiles.Change object
            #  - the second element being a str path to the changed item

            event_map: Dict[watchfiles.Change, Type[FileMonitorInputEvent]] = {
                watchfiles.Change.added: MonitoredFileWasCreatedInputEvent,
                watchfiles.Change.modified: MonitoredFileWasUpdatedInputEvent,
                watchfiles.Change.deleted: MonitoredFileWasDeletedOrMovedInputEvent,
            }

            for change in changes:
                change_type, change_path = change
                event_type = event_map.get(change_type)

                if not event_type:
                    self._logger.error(
                        "Unexpected event type in file change - %s", change_type
                    )
                    continue

                yield event_type(file=AsyncPath(change_path))

                # If the file has been deleted, commence watcher reset.
                if change_type == watchfiles.Change.deleted:
                    self._path_change_event.set()
