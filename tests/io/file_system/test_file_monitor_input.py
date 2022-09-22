#!/usr/bin/env python3

"""Tests for the FileMonitorInput, a part of the FileSystemMonitor module

This input watches for events occurring to regular files at one specific path.
Files at the selected path can be created, updated, or deleted on disk at
run-time, and the path selected for the input can also be changed.
"""

from __future__ import annotations

from typing import Optional, Type

import asyncio
import tempfile
import types

from aiopath.path import AsyncPath

import pytest

from mewbot.api.v1 import InputEvent
from mewbot.io.file_system.file_monitor import (
    FileMonitorInput,
    FileMonitorInputEvent,
    FileMonitorAcquiredInputEvent,
    MonitoredFileWasCreatedInputEvent,
    MonitoredFileWasUpdatedInputEvent,
    MonitoredFileWasDeletedOrMovedInputEvent,
)

from .utils import FileSystemTestUtilsDirEvents, FileSystemTestUtilsFileEvents


class FileMonitorTestHarnessGenerator:
    """Helper class that provides an async-context for testing the FileMonitorInput

    This is intended to be used with the `tempfile.TemporaryDirectory` context
    manager to handle creating a clean text environment.

    On entering the context, the Input is created, and its run function is scheduled
    as a test. A FileMonitorTestHarness object is returned, which provides methods
    to manipulate the file, and to check the next event in the queue is the correct
    type.

    On exiting the context, the run function is awaited (after calling shutdown) and
    we confirm that the queue is still empty, i.e. there were no unexpected trailing
    events.
    """

    directory: str
    name: str
    monitored_path: Optional[AsyncPath]

    inner: Optional[FileMonitorTestHarness] = None

    def __init__(self, temp_dir: str, name: str) -> None:
        self.directory = temp_dir
        self.name = name
        self.monitored_path = self.path

    @property
    def path(self) -> AsyncPath:
        """Get the path to the default test file,
        which is the one the Input is pre-configured to use"""
        return self._path(self.name)

    def _path(self, name: str) -> AsyncPath:
        """Get the path to a specific named file in the test folder"""
        return AsyncPath(self.directory, name)

    async def create_file(self, text: str = "", path: Optional[str] = None) -> AsyncPath:
        """Create the file which will be watched when the context is entered"""
        async_path = self._path(path or self.name)
        await async_path.write_text(text)

        return async_path

    async def create_dir(self, path: Optional[str] = None) -> None:
        """Create a directory in the temp folder, by default at the watched location."""
        async_path = self._path(path or self.name)
        if await async_path.exists():
            raise FileExistsError

        await async_path.mkdir()

    async def __aenter__(self) -> FileMonitorTestHarness:
        self.inner = FileMonitorTestHarness(self.path, self.name, self.monitored_path)
        return self.inner

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: types.TracebackType,
    ) -> None:
        if not self.inner:
            return

        events = []

        await self.inner.input.shutdown()
        await asyncio.wait_for(self.inner.task, 2.5)

        exception = self.inner.task.exception()

        if exception:
            raise exception

        while True:
            try:
                events.append(self.inner.queue.get_nowait())
            except asyncio.QueueEmpty:
                break

        assert not events, "Extra events in test harness"


class FileMonitorTestHarness:
    """Testing class created by the FileMonitorTestHarnessGenerator context manager

    Provides methods to manipulate the file, and to check the next event in the
    queue is the correct type, and return it to the test for further validation."""

    tempdir: tempfile.TemporaryDirectory[str]
    input: FileMonitorInput
    queue: asyncio.Queue[InputEvent]
    task: asyncio.Task[None]
    path: AsyncPath

    def __init__(self, path: AsyncPath, name: str, monitored_path: Optional[AsyncPath]):
        self.path = path
        self.queue = asyncio.Queue()
        self.input = FileMonitorInput(monitored_path)
        self.input.bind(self.queue)
        self.task = asyncio.get_running_loop().create_task(self.input.run(), name=name)

    async def create_dir(self) -> None:
        """Create a directory in the default-watched location"""
        if await self.path.exists():
            raise FileExistsError

        await self.path.mkdir()

    async def create_file(self, content: str = "") -> None:
        """Create a file in the default-watched location"""
        if await self.path.exists():
            raise FileExistsError

        await self.path.write_text(content)

    async def update_file(self, content: str = "", must_exist: bool = False) -> None:
        """Create or Update a file in the default-watched location"""
        if must_exist and not await self.path.exists():
            raise FileExistsError

        await self.path.write_text(content)

    async def delete_file(self) -> None:
        """Delete the file in the default-watched location"""
        if not await self.path.exists():
            raise FileExistsError

        if await self.path.is_dir():
            await self.path.rmdir()
        else:
            await self.path.unlink()

    async def expect_event(self, *typed: Type[FileMonitorInputEvent]) -> InputEvent:
        """Confirm that the next even in the queue is one of the provided types
        If the queue does not receive within half a second, an exception is thrown."""
        try:
            event = await asyncio.wait_for(self.queue.get(), 0.5)
        except asyncio.exceptions.TimeoutError as err:
            raise Exception(
                "No event received waiting for " + "|".join(t.__name__ for t in typed)
            ) from err

        assert isinstance(event, typed)
        return event

    async def expect_no_events(self) -> Optional[InputEvent]:
        """Confirm that no more events are pending. This function waits for half a second"""
        try:
            return await asyncio.wait_for(self.queue.get(), 0.5)
        except asyncio.exceptions.TimeoutError:
            return None


class TestFileMonitorInput(FileSystemTestUtilsDirEvents, FileSystemTestUtilsFileEvents):
    ############################################################################
    # Init and attributes
    ############################################################################

    def test_init_with_no_path(self) -> None:
        """
        Tests that we can start an isolated copy of FileMonitorInput - for testing purposes.
        input_path is set to None
        """
        test_fs_input = FileMonitorInput(path=None)
        assert isinstance(test_fs_input, FileMonitorInput)
        assert test_fs_input.input_path is None

    def test_init_with_slash_path(self) -> None:
        """
        Tests that we can start an isolated copy of FileMonitorInput - for testing purposes.
        input_path is set to "/"
        """
        test_fs_input = FileMonitorInput(path=AsyncPath("/"))
        assert isinstance(test_fs_input, FileMonitorInput)
        assert test_fs_input.input_path == "/"

    ############################################################################
    # Acquiring The Watcher
    ############################################################################

    @pytest.mark.asyncio
    async def test_no_acquisition_on_null_path(self) -> None:
        """
        Tests that we can start an isolated copy of FileMonitorInput - for testing purposes.

        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            generator = FileMonitorTestHarnessGenerator(tmp_dir_path, "none-path")
            generator.monitored_path = None

            async with generator as harness:
                assert harness.input.input_path is None
                assert harness.input._monitored_path is None
                assert await harness.expect_no_events() is None

    @pytest.mark.asyncio
    async def test_no_acquisition_on_blank_dir(self) -> None:
        """
        Tests that we can start an isolated copy of FileMonitorInput - for testing purposes.

        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            async with FileMonitorTestHarnessGenerator(tmp_dir_path, "no-action") as harness:
                assert await harness.expect_no_events() is None

    @pytest.mark.asyncio
    async def test_acquire_watcher_on_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            generator = FileMonitorTestHarnessGenerator(tmp_dir_path, "acquire-file")
            await generator.create_file("hello")
            async with generator as harness:
                await harness.expect_event(FileMonitorAcquiredInputEvent)

    @pytest.mark.asyncio
    async def test_acquire_watcher_on_file_creation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            generator = FileMonitorTestHarnessGenerator(tmp_dir_path, "acquire-created-file")
            async with generator as harness:
                await harness.create_file("hello")
                await harness.expect_event(MonitoredFileWasCreatedInputEvent)
                await harness.expect_event(FileMonitorAcquiredInputEvent)

    @pytest.mark.asyncio
    async def test_acquire_watcher_on_replacing_dir_with_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            generator = FileMonitorTestHarnessGenerator(tmp_dir_path, "acquire-created-file")
            await generator.create_dir()
            async with generator as harness:
                assert await harness.expect_no_events() is None

                await harness.delete_file()
                assert await harness.expect_no_events() is None

                await harness.create_file("hello")
                await harness.expect_event(MonitoredFileWasCreatedInputEvent)
                await harness.expect_event(FileMonitorAcquiredInputEvent)

    ############################################################################
    # Changing Requested File
    ############################################################################

    @pytest.mark.asyncio
    async def test_acquire_watcher_on_second_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            generator = FileMonitorTestHarnessGenerator(tmp_dir_path, "acquire-file")
            path_old = await generator.create_file("hello")
            path_new = await generator.create_file("goodbye", path="new")

            async with generator as harness:
                event = await harness.expect_event(FileMonitorAcquiredInputEvent)
                assert isinstance(event, FileMonitorAcquiredInputEvent)
                assert event.path == str(path_old)

                harness.input.input_path = str(path_new)
                event = await harness.expect_event(FileMonitorAcquiredInputEvent)
                assert isinstance(event, FileMonitorAcquiredInputEvent)
                assert event.path == str(path_new)

                await harness.delete_file()
                assert await harness.expect_no_events() is None

    ############################################################################
    # Manipulating the file (one time)
    ############################################################################

    @pytest.mark.asyncio
    async def test_update_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            generator = FileMonitorTestHarnessGenerator(tmp_dir_path, "acquire-created-file")
            await generator.create_file("hello")

            async with generator as harness:
                await harness.expect_event(FileMonitorAcquiredInputEvent)

                await harness.update_file("goodbye", must_exist=True)
                await harness.expect_event(MonitoredFileWasUpdatedInputEvent)

    @pytest.mark.asyncio
    async def test_update_created_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            generator = FileMonitorTestHarnessGenerator(tmp_dir_path, "acquire-created-file")
            async with generator as harness:
                await harness.create_file("hello")
                await harness.expect_event(MonitoredFileWasCreatedInputEvent)
                await harness.expect_event(FileMonitorAcquiredInputEvent)

                await harness.update_file("goodbye", must_exist=True)
                await harness.expect_event(MonitoredFileWasUpdatedInputEvent)

    @pytest.mark.asyncio
    async def test_delete_created_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            generator = FileMonitorTestHarnessGenerator(tmp_dir_path, "acquire-created-file")
            async with generator as harness:
                await harness.create_file("hello")
                await harness.expect_event(MonitoredFileWasCreatedInputEvent)
                await harness.expect_event(FileMonitorAcquiredInputEvent)

                await harness.delete_file()
                event = await harness.expect_event(
                    MonitoredFileWasUpdatedInputEvent,
                    MonitoredFileWasDeletedOrMovedInputEvent,
                )
                if isinstance(event, MonitoredFileWasUpdatedInputEvent):
                    await harness.expect_event(MonitoredFileWasDeletedOrMovedInputEvent)

    @pytest.mark.asyncio
    async def test_delete_and_recreate_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            generator = FileMonitorTestHarnessGenerator(tmp_dir_path, "acquire-created-file")
            await generator.create_file("hello")

            async with generator as harness:
                await harness.expect_event(FileMonitorAcquiredInputEvent)

                await harness.delete_file()
                await harness.update_file("hello")

                event = await harness.expect_event(
                    MonitoredFileWasUpdatedInputEvent,
                    MonitoredFileWasDeletedOrMovedInputEvent,
                )
                if isinstance(event, MonitoredFileWasUpdatedInputEvent):
                    await harness.expect_event(MonitoredFileWasDeletedOrMovedInputEvent)

                await harness.expect_event(MonitoredFileWasCreatedInputEvent)
                await harness.expect_event(FileMonitorAcquiredInputEvent)

    @pytest.mark.asyncio
    async def test_delete_and_recreate_file_with_delay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            generator = FileMonitorTestHarnessGenerator(tmp_dir_path, "acquire-created-file")
            await generator.create_file("hello")

            async with generator as harness:
                await harness.expect_event(FileMonitorAcquiredInputEvent)

                await harness.delete_file()

                event = await harness.expect_event(
                    MonitoredFileWasUpdatedInputEvent,
                    MonitoredFileWasDeletedOrMovedInputEvent,
                )
                if isinstance(event, MonitoredFileWasUpdatedInputEvent):
                    await harness.expect_event(MonitoredFileWasDeletedOrMovedInputEvent)

                await asyncio.sleep(0.5)
                await harness.update_file("hello")
                await harness.expect_event(MonitoredFileWasCreatedInputEvent)
                await harness.expect_event(FileMonitorAcquiredInputEvent)

    ############################################################################
    # Manipulating the file (repeatedly)
    ############################################################################

    @pytest.mark.asyncio
    async def test_update_existing_file_repeatedly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            generator = FileMonitorTestHarnessGenerator(tmp_dir_path, "acquire-created-file")
            await generator.create_file("hello")

            async with generator as harness:
                await harness.expect_event(FileMonitorAcquiredInputEvent)

                for _ in range(10):
                    await harness.update_file("goodbye", must_exist=True)
                    await harness.expect_event(MonitoredFileWasUpdatedInputEvent)
