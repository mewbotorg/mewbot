#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests for 'file_storage' IO module, used for writing to the file system.
"""

from __future__ import annotations

import logging
import tempfile

import pytest

from base import FileStorageTestFixture

from mewbot.api.v1 import OutputEvent
from mewbot.io.file_storage import (
    FileStorage,
    FileStorageOutput,
    FSOutputEvent,
    CreateDirectoryOutputEvent,
    WriteToFileOutputEvent,
    DeleteFileOutputEvent,
)


class TestFileTypeFileStorage(FileStorageTestFixture):
    """
    File Storage test cases: handle non-output event test cases.
    """

    async def test_config_init_no_path(self) -> None:
        """
        File Storage test case: check that creation of the config with a path.

        Result should be a config with the given path, that reports the path as existing.
        """

        with pytest.raises(ValueError, match="FileStorage initialised without path"):
            FileStorage()

    async def test_config_init(self) -> None:
        """
        File Storage test case: check that creation of the config with a path.

        Result should be a config with the given path, that reports the path as existing.
        """

        config = FileStorage(path=self.path)

        assert config.path == self.path
        assert config.path_exists

        inputs = config.get_inputs()
        assert isinstance(inputs, list)
        assert len(inputs) == 0

        outputs = config.get_outputs()
        assert isinstance(outputs, list)
        assert len(outputs) == 1

        output = outputs[0]
        assert isinstance(output, FileStorageOutput)
        assert output.path == self.path
        assert output.path_exists

    async def test_config_init_with_no_node(self) -> None:
        """
        File Storage test case: creation with a non-existent path.

        Result should be a config with the given path, that reports the path as not existing.
        """

        file_path = tempfile.mktemp(dir=self.path)
        config = FileStorage(path=file_path)

        assert config.path == file_path
        assert not config.path_exists

        outputs = config.get_outputs()
        assert isinstance(outputs, list)
        assert len(outputs) == 1

        output = outputs[0]
        assert isinstance(output, FileStorageOutput)
        assert output.path == file_path
        assert not output.path_exists

    async def test_output_init_with_file(self) -> None:
        """
        File Storage test case: creation with a path that exists as a file.

        Result should be a config with the given path, that reports the path
        as not existing, as it is not a directory.
        """

        file_path = tempfile.mktemp(dir=self.path)

        with open(file_path, "wb") as write:
            write.write(b"")

        config = FileStorage(path=file_path)

        assert config.path == file_path
        assert not config.path_exists

        outputs = config.get_outputs()
        assert isinstance(outputs, list)
        assert len(outputs) == 1

        output = outputs[0]
        assert isinstance(output, FileStorageOutput)
        assert output.path == file_path
        assert not output.path_exists

    async def test_output_update_path(self) -> None:
        """
        File Storage test case: changing the specified path on the fly.

        We confirm that the path value is updated in both the config and in
        the output. We also check that the existence check also updates dynamically.
        """

        config = FileStorage(path=tempfile.gettempdir())
        output = config.get_outputs()[0]

        assert isinstance(output, FileStorageOutput)

        assert config.path == tempfile.gettempdir()
        assert output.path == tempfile.gettempdir()
        assert config.path_exists
        assert output.path_exists

        config.path = self.path
        assert config.path == self.path
        assert output.path == self.path
        assert config.path_exists
        assert output.path_exists

        path = self.path + "ssss"
        config.path = path
        assert config.path == path
        assert output.path == path
        assert not config.path_exists
        assert not output.path_exists

        config.path = self.path
        assert config.path == self.path
        assert output.path == self.path
        assert config.path_exists
        assert output.path_exists

    def test_output_event_types(self) -> None:
        """
        File Storage test case: confirm the expected event types are in the output.
        """

        output = FileStorageOutput(tempfile.gettempdir())
        events = output.consumes_outputs()

        assert isinstance(events, set)
        assert len(events) == 3
        assert WriteToFileOutputEvent in events
        assert DeleteFileOutputEvent in events
        assert CreateDirectoryOutputEvent in events

    async def test_output_event_bad_event(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        File Storage test case: Attempt to output an invalid event.
        """

        bad_path = tempfile.mktemp(dir=self.path)

        output = FileStorageOutput(bad_path)
        event = OutputEvent()

        with caplog.at_level(logging.WARNING, self.logger.name):
            assert not await output.output(event)

        assert len(caplog.records) == 1
        assert caplog.records[0].msg == "Received unexpected event type %s"

    async def test_output_event_bad_base_event(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        File Storage test case: attempt to output the base FSOutputEvent.

        This should fail with by not handling the event, logging an error.
        """

        output = FileStorageOutput(self.path)
        event = FSOutputEvent(self.path)

        with caplog.at_level(logging.INFO, self.logger.name):
            assert not await output.output(event)

        assert len(caplog.records) == 1
        assert caplog.records[0].msg == "Received unexpected event type %s"
