#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause


"""
Tests for 'file_storage' IO module, used for writing to the file system.

This class tests the behaviours of the WriteToFileOutputEvent.
"""

import os
import tempfile

from base import FileStorageTestFixture
from mewbot.io.file_storage import CreateDirectoryOutputEvent


class TestCreateDirectoryOutputEventHandling(FileStorageTestFixture):
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the CreateDirectoryOutputEvent.
    """

    async def test_output_create_dir(self) -> None:
        """
        File Storage test case: create a directory.

        The event should succeed and the directory will be created.
        """

        file_path = tempfile.mktemp(dir=self.path)

        assert not os.path.exists(file_path)
        assert not os.path.isdir(file_path)

        event = CreateDirectoryOutputEvent(path=file_path)
        assert await self.output.output(event)

        assert os.path.exists(file_path)
        assert os.path.isdir(file_path)

    async def test_output_create_nested_dir(self) -> None:
        """
        File Storage test case: .

        FIXME: Write this
        """

        file_path = tempfile.mktemp(dir=self.path + "/foo")

        event = CreateDirectoryOutputEvent(path=file_path)
        assert await self.output.output(event)

        assert os.path.exists(file_path)
        assert os.path.isdir(file_path)

    async def test_output_create_existing_dir(self) -> None:
        """
        File Storage test case: .

        FIXME: Write this
        """

        file_path = tempfile.mktemp(dir=self.path)

        os.mkdir(file_path)

        event = CreateDirectoryOutputEvent(path=file_path)
        assert await self.output.output(event)

        assert os.path.exists(file_path)
        assert os.path.isdir(file_path)

    async def test_output_create_parent_dir(self) -> None:
        """
        File Storage test case: .

        FIXME: Write this
        """

        file_path = self.path + "/.."

        event = CreateDirectoryOutputEvent(path=file_path)
        assert not await self.output.output(event)

        assert os.path.exists(file_path)
        assert os.path.isdir(file_path)
