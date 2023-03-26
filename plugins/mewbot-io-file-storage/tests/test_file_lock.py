#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests for 'file_storage' IO module, used for writing to the file system.
"""

from __future__ import annotations

import asyncio
import fcntl
import sys
import tempfile

import aiofiles
import pytest

from base import FileStorageTestFixture

from mewbot.io.file_storage import AsyncFileLock


class TestAsyncFileLock(FileStorageTestFixture):
    """
    Tests for the AsyncFileLock that forms part of the file-storage.
    """

    async def test_basic_lock(self) -> None:
        """
        File Lock test case: open, lock, and write to a file.

        The file contents should be successfully written
        """

        file_path = tempfile.mktemp(dir=self.path)

        async with aiofiles.open(file_path, "w", encoding="utf-8") as test_handle:
            lock = AsyncFileLock(test_handle)

            async with lock:
                await test_handle.write("hello")

        with open(file_path, "r", encoding="utf-8") as read_handle:
            assert read_handle.read() == "hello"

    async def test_lock_timeout(self) -> None:
        """
        File Lock test case: attempt to lock a file that is already locked.

        The lock should fail due to timeout.
        """

        file_path = tempfile.mktemp(dir=self.path)

        # First, ensure the file exists
        with open(file_path, "w", encoding="utf-8"):
            pass

        with open(file_path, "r", encoding="utf-8") as read_handle:
            fcntl.flock(read_handle.fileno(), fcntl.LOCK_SH)

            async with aiofiles.open(file_path, "w") as test_handle:
                lock = AsyncFileLock(test_handle, 0.5)

                error = TimeoutError if sys.version_info.minor > 9 else asyncio.TimeoutError
                with pytest.raises(error):
                    await lock.acquire()

    async def test_lock_before_timeout(self) -> None:
        """
        File Lock test case: attempt to lock a file that is already locked, but gets unlocked.

        The lock should not be acquired before the file is unlocked.
        """

        loop = asyncio.get_running_loop()

        file_path = tempfile.mktemp(dir=self.path)

        # First, ensure the file exists
        with open(file_path, "w", encoding="utf-8"):
            pass

        with open(file_path, "r", encoding="utf-8") as read_handle:
            fcntl.flock(read_handle.fileno(), fcntl.LOCK_SH)

            async with aiofiles.open(file_path, "w") as test_handle:
                lock = AsyncFileLock(test_handle, 0.6)
                task = loop.create_task(lock.acquire())

                await asyncio.sleep(0.2)
                assert not task.done()

                fcntl.flock(read_handle.fileno(), fcntl.LOCK_UN)
                await task
