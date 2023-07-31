# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

# Aim is to run, in sections, as many of the input methods as possible
# Including running a full bot with logging triggers and actions.
# However, individual components also have to be isolated for testing purposes.

"""
Tests the dir input - monitors a directory for changes.
"""


import os
import tempfile

import pytest

from mewbot.io.file_system_monitor.fs_events import (
    DirCreatedWithinWatchedDirFSInputEvent,
    DirUpdatedAtWatchLocationFSInputEvent,
    DirUpdatedWithinWatchedDirFSInputEvent,
    FileCreatedWithinWatchedDirFSInputEvent,
    FileDeletedWithinWatchedDirFSInputEvent,
    FileUpdatedWithinWatchedDirFSInputEvent,
)

from ..fs_test_utils import FileSystemTestUtilsDirEvents, FileSystemTestUtilsFileEvents

# pylint: disable=invalid-name
# for clarity, test functions should be named after the things they test
# which means CamelCase in function names

# pylint: disable=duplicate-code
# Due to testing for the subtle differences between how the monitors respond in windows and
# linux, code has - inevitably - ended up very similar.
# As such, this inspection has had to be disabled.


class TestDirTypeFSInputGenericTests(
    FileSystemTestUtilsDirEvents, FileSystemTestUtilsFileEvents
):
    """
    Tests which should respond the same on any operating system.

    (Ideally, eventually, this will be _all_ of them - but we need some diagnostics as the
    underlying apis do behave differently on different systems).
    """

    # DIRS IN DIRS

    @pytest.mark.asyncio
    async def test_DirTypeFSInput_existing_dir_create_dir(self) -> None:
        """
        Check for the expected created signal from a dir which is created in a monitored dir.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            run_task, output_queue, _ = await self.get_DirTypeFSInput(tmp_dir_path)

            # - Using blocking methods - this should still work
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            os.mkdir(new_dir_path)
            # We expect a directory creation event to be registered inside the watched dir
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedWithinWatchedDirFSInputEvent,
            )

            await self.cancel_task(run_task)

    # FILES IN DIRS

    @pytest.mark.asyncio
    async def test_DirTypeFSInput_existing_dir_crefile(self) -> None:
        """
        Start in an existing dir - then create a file in it.

        Check for the expected created signal from a file which is created in a monitored dir.
        Followed by an attempt to update the file.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output_queue, _ = await self.get_DirTypeFSInput(tmp_dir_path)

            # - Using blocking methods - this should still work
            new_file_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            with open(new_file_path, "w", encoding="utf-16") as output_file:
                output_file.write("Here we go")
            await self.process_file_event_queue_response(
                output_queue=output_queue,
                file_path=new_file_path,
                event_type=FileCreatedWithinWatchedDirFSInputEvent,
            )

    @pytest.mark.asyncio
    async def test_DirTypeFSInput_existing_dir_cre_ud_file_del_file(self) -> None:
        """
        Start in an existing dir - then create and update a file.

        Check for the expected created signal from a file which is created in a monitored dir.
        Followed by an attempt to update the file.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            run_task, output_queue, _ = await self.get_DirTypeFSInput(tmp_dir_path)

            # - Using blocking methods - this should still work
            new_file_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            with open(new_file_path, "w", encoding="utf-16") as output_file:
                output_file.write("Here we go")
            await self.process_file_event_queue_response(
                output_queue=output_queue,
                file_path=new_file_path,
                event_type=FileCreatedWithinWatchedDirFSInputEvent,
            )

            with open(new_file_path, "a", encoding="utf-16") as output_file:
                output_file.write("Here we go again")

            # The directory we're watching itself has been updated with the file change
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=tmp_dir_path,
                allowed_queue_size=1,
                event_type=DirUpdatedAtWatchLocationFSInputEvent,
            )

            # The file has also been updated
            await self.process_file_event_queue_response(
                output_queue=output_queue,
                file_path=new_file_path,
                event_type=FileUpdatedWithinWatchedDirFSInputEvent,
            )

            # Now delete the file
            os.unlink(new_file_path)

            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=tmp_dir_path,
                allowed_queue_size=1,
                event_type=DirUpdatedWithinWatchedDirFSInputEvent,
            )

            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_file_path,
                allowed_queue_size=1,
                event_type=FileDeletedWithinWatchedDirFSInputEvent,
            )

            await self.cancel_task(run_task)
