#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests for 'file_storage' IO module, used for writing to the file system.

This class tests the behaviours of the DeleteFileOutputEvent.
"""

import logging
import os
import tempfile

import pytest

from base import FileStorageTestFixture
from mewbot.io.file_storage import DeleteFileOutputEvent


class TestDeleteFileOutputEventHandling(FileStorageTestFixture):
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the DeleteFileOutputEvent.
    """

    async def test_delete_event_when_no_dir(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        File Storage test case: attempt to delete a non-existent file.

        The output should mark the event as not processed.
        """

        bad_path = tempfile.mktemp(dir=self.path)
        event = DeleteFileOutputEvent(path=bad_path)

        with caplog.at_level(logging.INFO, self.logger.name):
            assert not await self.output.output(event)

        assert len(caplog.records) == 1
        assert logging.WARNING == caplog.records[0].levelno
        assert "Unable to delete non-existent path %s" in caplog.records[0].msg

    async def test_output_unlink_file(self) -> None:
        """
        File Storage test case: delete a file which exists in the tree.

        This should successfully delete the file.
        """

        file_path = tempfile.mktemp(dir=self.path)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("")

        event = DeleteFileOutputEvent(path=file_path)
        assert await self.output.output(event)

        assert not os.path.exists(file_path)

    async def test_output_unlink_dir(self) -> None:
        """
        File Storage test case: deleting a directory.

        The output event will currently cause an exception
        FIXME: This should be handled and logged rather than raising.
        """

        file_path = tempfile.mktemp(dir=self.path)

        os.mkdir(file_path)

        with pytest.raises(IsADirectoryError):
            event = DeleteFileOutputEvent(path=file_path)
            assert await self.output.output(event)

    async def test_output_unlink_missing_file(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        File Storage test case: deleting a file that does not exist.

        The output event will be rejected, creating a warning-level log message.
        """

        file_path = tempfile.mktemp(dir=self.path)

        event = DeleteFileOutputEvent(path=file_path)

        with caplog.at_level(logging.INFO, self.logger.name):
            assert not await self.output.output(event)

        assert len(caplog.records) == 1
        assert "Unable to delete non-existent path %s" in caplog.records[0].msg
        assert logging.WARNING == caplog.records[0].levelno
        assert not os.path.exists(file_path)
