#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause


"""
Tests for 'file_storage' IO module, used for writing to the file system.

This class tests the behaviours of the WriteToFileOutputEvent.
"""

import logging
import os
import tempfile

import pytest

from base import FileStorageTestFixture
from mewbot.io.file_storage import WriteToFileOutputEvent


class TestCreateDirectoryOutputEventHandling(FileStorageTestFixture):
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the WriteToFileOutputEvent.
    """

    async def test_output_create_file_str(self) -> None:
        """
        File Storage test case: write a fixed string to a file.

        The event should be processed, and the file exist with the written contents.
        """

        file_path = tempfile.mktemp(dir=self.path)
        contents = "Hello"

        event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
        assert await self.output.output(event)

        assert os.path.exists(file_path)

        with open(file_path, encoding="utf-8") as file:
            assert file.read() == contents

    async def test_output_create_nested_file_str(self) -> None:
        """
        File Storage test case: write a fixed string to a file in a sub folder.

        The event should be processed, with the intermediate folder being
        auto-created, and the file exist with the written contents.
        """

        file_path = self.path + "/foo/bar"
        contents = "Hello"

        event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
        assert await self.output.output(event)

        assert os.path.exists(file_path)

        with open(file_path, encoding="utf-8") as file:
            assert file.read() == contents

    async def test_output_create_file_bytes(self) -> None:
        """
        File Storage test case: .


        """

        file_path = tempfile.mktemp(dir=self.path)
        contents = b"Hello"

        event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
        assert await self.output.output(event)

        assert os.path.exists(file_path)
        with open(file_path, "rb") as file:
            assert file.read() == contents

    async def test_output_write_file_root(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        File Storage test case: .

        FIXME: Write this
        """

        file_path = tempfile.mktemp(dir="/")
        event = WriteToFileOutputEvent(path=file_path, file_contents="Hello")

        with caplog.at_level(logging.WARNING, self.logger.name):
            assert not await self.output.output(event)

        assert len(caplog.records) == 1
        assert caplog.records[0].msg == self.ERROR_MESSAGE_OUTSIDE_BASE_PATH
        assert not os.path.exists(file_path)

    async def test_output_write_file_relative(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        File Storage test case: .

        FIXME: Write this
        """

        file_path = self.path + "/../foo"

        event = WriteToFileOutputEvent(
            path=file_path,
            file_contents="Hello",
        )

        with caplog.at_level(logging.WARNING, self.logger.name):
            assert not await self.output.output(event)

        assert len(caplog.records) == 1
        assert caplog.records[0].msg == self.ERROR_MESSAGE_OUTSIDE_BASE_PATH
        assert not os.path.exists(file_path)
        assert not os.path.exists(file_path)

    async def test_output_create_file_overwrite(self) -> None:
        """
        File Storage test case: .

        FIXME: write this
        """

        file_path = tempfile.mktemp(dir=self.path)
        initial_contents = "Hello"
        contents = "Goodbye"

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(initial_contents)

        event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
        assert await self.output.output(event)

        assert os.path.exists(file_path)
        with open(file_path, encoding="utf-8") as file:
            assert file.read() == contents

    async def test_output_create_file_no_overwrite(self) -> None:
        """
        File Storage test case: .

        FIXME: write this
        """

        file_path = tempfile.mktemp(dir=self.path)
        initial_contents = "Hello"
        contents = "Goodbye"

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(initial_contents)

        event = WriteToFileOutputEvent(
            path=file_path, file_contents=contents, may_overwrite=False
        )
        assert not await self.output.output(event)

        with open(file_path, encoding="utf-8") as file:
            assert file.read() == initial_contents

    async def test_output_create_file_append(self) -> None:
        """
        File Storage test case: .


        """

        file_path = tempfile.mktemp(dir=self.path)
        contents_1 = "Hello"
        contents_2 = "Goodbye"

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(contents_1)

        event = WriteToFileOutputEvent(path=file_path, file_contents=contents_2, append=True)
        assert await self.output.output(event)

        assert os.path.exists(file_path)
        with open(file_path, encoding="utf-8") as file:
            assert file.read() == contents_1 + contents_2
