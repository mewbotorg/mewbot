#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause


"""
Tests for 'file_storage' IO module, used for writing to the file system.

This is the base test class with configuration fixtures.
"""

import logging
import tempfile

from mewbot.io.file_storage import FileStorage, FileStorageOutput


class FileStorageTestFixture:
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the CreateDirectoryOutputEvent.
    """

    ERROR_MESSAGE_OUTSIDE_BASE_PATH = (
        "Refusing to write to %s, as it would result in a file outside of %s"
    )

    temp_dir: tempfile.TemporaryDirectory[str]
    path: str
    io_config: FileStorage
    output: FileStorageOutput
    logger: logging.Logger

    @classmethod
    def setup_class(cls) -> None:
        """
        Set up an environment for the test run.

        This class tests the behaviours of the CreateDirectoryOutputEvent.
        """

        cls.temp_dir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        cls.path = cls.temp_dir.name
        cls.io_config = FileStorage(path=cls.path)
        cls.output = cls.io_config.get_outputs()[0]
        # noinspection PyProtectedMember
        cls.logger = cls.output._logger  # pylint: disable=protected-access

    @classmethod
    def teardown_class(cls) -> None:
        """
        Clean up the temporary directory from this test run.
        """
        cls.temp_dir.cleanup()
