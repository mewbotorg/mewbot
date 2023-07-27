# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

# Aim is to run, in sections, as many of the input methods as possible
# Including running a full bot with logging triggers and actions.
# However, individual components also have to be isolated for testing purposes.

"""
Tests the dir input - monitors a directory for changes.
"""


import asyncio
import os
import shutil
import sys
import tempfile
import uuid

import pytest

from mewbot.io.file_system_monitor.fs_events import (
    DirCreatedAtWatchLocationFSInputEvent,
    DirCreatedWithinWatchedDirFSInputEvent,
    DirDeletedFromWatchedDirFSInputEvent,
    DirDeletedFromWatchLocationFSInputEvent,
    DirUpdatedAtWatchLocationFSInputEvent,
    DirUpdatedWithinWatchedDirFSInputEvent,
DirMovedWithinWatchedDirFSInputEvent,
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


class TestDirTypeFSInput(FileSystemTestUtilsDirEvents, FileSystemTestUtilsFileEvents):
    """
    Tests the DirTypeFSInput input type.
    """


    # - RUNNING TO DETECT DIR CHANGES


    @pytest.mark.asyncio
    async def testDirTypeFSInput_existing_dir_create_dir_del_dir(self) -> None:
        """
        Check for the expected created signal from a dir which is created in a monitored dir.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            run_task, output_queue, _ = await self.get_DirTypeFSInput(tmp_dir_path)

            # - Using blocking methods - this should still work
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            # Create the dir - check for the response
            os.mkdir(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedWithinWatchedDirFSInputEvent,
            )

            # Delete the dir - check for the response
            shutil.rmtree(new_dir_path)

            # - we should see an update to the monitored directory
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=tmp_dir_path,
                event_type=DirUpdatedWithinWatchedDirFSInputEvent,
            )

            # - we should then see a deletion event within the monitored dir
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirDeletedFromWatchedDirFSInputEvent,
            )

            await self.cancel_task(run_task)

    @pytest.mark.asyncio
    async def testDirTypeFSInput_existing_dir_create_dir_del_dir_starting_non_exist_dir(
        self,
    ) -> None:
        """
        Start without a directory at the path - then create one and run the test.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            run_task, output_queue, _ = await self.get_DirTypeFSInput(tmp_dir_path)

            # - Using blocking methods - this should still work
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            # Create the dir - check for the response
            os.mkdir(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedWithinWatchedDirFSInputEvent,
            )

            # Delete the dir - check for the response
            shutil.rmtree(new_dir_path)

            # - we should see an update to the monitored directory
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=tmp_dir_path,
                event_type=DirUpdatedWithinWatchedDirFSInputEvent,
            )

            # - we should then see a deletion event within the monitored dir
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirDeletedFromWatchedDirFSInputEvent,
            )

            await self.cancel_task(run_task)

    @pytest.mark.asyncio
    async def testDirTypeFSInput_non_existing_dir_create_dir_del_dir(self) -> None:
        """
        Check for the expected created signal from a dir which is created in a monitored dir.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            run_task, output_queue, _ = await self.get_DirTypeFSInput(new_dir_path)

            # Create the dir - check for the response
            os.mkdir(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedAtWatchLocationFSInputEvent,
            )

            # Delete the dir - check for the response
            shutil.rmtree(new_dir_path)

            # - we should see an update to the monitored directory
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirDeletedFromWatchLocationFSInputEvent,
            )

            await self.cancel_task(run_task)

    @pytest.mark.asyncio
    async def testDirTypeFSInput_non_existing_dir_create_dir_del_dir_set_watch_None(
        self,
    ) -> None:
        """
        Unexpectedly set the input path to be None, and then monitor dir watcher.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            run_task, output_queue, test_fs_input = await self.get_DirTypeFSInput(
                new_dir_path
            )

            # Create the dir - check for the response
            os.mkdir(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedAtWatchLocationFSInputEvent,
            )

            # Delete the dir - check for the response
            shutil.rmtree(new_dir_path)

            # - we should see an update to the monitored directory
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirDeletedFromWatchLocationFSInputEvent,
            )

            # Try and break things
            test_fs_input.input_path = None
            run_task_2 = asyncio.get_running_loop().create_task(test_fs_input.run())

            await self.cancel_task(run_task)
            await self.cancel_task(run_task_2)

    @pytest.mark.asyncio
    async def testDirTypeFSInput_non_existing_dir_create_dir_del_dir_set_ip_None(
        self,
    ) -> None:
        """
        Unexpectedly set the input path to be None, and then monitor dir watcher.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            run_task, output_queue, test_fs_input = await self.get_DirTypeFSInput(
                new_dir_path
            )

            # Create the dir - check for the response
            os.mkdir(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedAtWatchLocationFSInputEvent,
            )

            # Delete the dir - check for the response
            shutil.rmtree(new_dir_path)

            # - we should see an update to the monitored directory
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirDeletedFromWatchLocationFSInputEvent,
            )

            # Try and break things
            test_fs_input._input_path = None
            run_task_2 = asyncio.get_running_loop().create_task(
                test_fs_input.monitor_input_path()
            )

            run_task_3 = asyncio.get_running_loop().create_task(
                test_fs_input.file_system_observer.monitor_dir_watcher()
            )
            assert await self.cancel_task(run_task_3) is None  # type: ignore

            # Try and interfere with the observer directly
            test_fs_input.file_system_observer._input_path = None

            run_task_4 = asyncio.get_running_loop().create_task(
                test_fs_input.file_system_observer.monitor_dir_watcher()
            )

            await self.cancel_task(run_task)
            await self.cancel_task(run_task_2)
            # The observer has been sabotaged. This should fail.
            try:
                await self.cancel_task(run_task_4)  # type: ignore
            except NotImplementedError:
                pass

    @pytest.mark.asyncio
    async def testDirTypeFSInput_monitor_dir_watcher_normal_operation(
        self,
    ) -> None:
        """
        Unexpectedly set the input path to be None, and then monitor dir watcher.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            run_task, output_queue, test_fs_input = await self.get_DirTypeFSInput(
                new_dir_path
            )

            # There's no path, so there is currently no observer
            assert not hasattr(test_fs_input, "file_system_observer")

            # Create the dir - check for the response
            os.mkdir(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedAtWatchLocationFSInputEvent,
            )

            run_task = asyncio.get_running_loop().create_task(
                test_fs_input.file_system_observer.monitor_dir_watcher()  # type: ignore
            )

            shutil.rmtree(new_dir_path)

            assert await self.cancel_task(run_task) is None  # type: ignore

    @pytest.mark.asyncio
    async def testDirTypeFSInput_monitor_dir_watcher_file_created(
        self,
    ) -> None:
        """
        Set up a dir watcher - then create a file where it expects a dr.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            run_task, output_queue, test_fs_input = await self.get_DirTypeFSInput(
                new_dir_path
            )

            # There's no path, so there is currently no observer
            assert not hasattr(test_fs_input, "file_system_observer")

            # Create the dir - check for the response - there should be none
            with open(new_dir_path, "w", encoding="utf-8") as test_out_file:
                test_out_file.write(str(uuid.uuid4()))

            try:
                await self.process_dir_event_queue_response(
                    output_queue=output_queue,
                    dir_path=new_dir_path,
                    event_type=DirCreatedAtWatchLocationFSInputEvent,
                )
            except asyncio.exceptions.TimeoutError:
                pass

    @pytest.mark.asyncio
    async def testDirTypeFSInput_monitor_dir_unexpectdaly_nullify_queue(
        self,
    ) -> None:
        """
        Unexpectedly set the input path to be None, and then monitor dir watcher.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            run_task, output_queue, test_fs_input = await self.get_DirTypeFSInput(
                new_dir_path
            )

            # There's no path, so there is currently no observer
            assert not hasattr(test_fs_input, "file_system_observer")

            # Create the dir - check for the response
            os.mkdir(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedAtWatchLocationFSInputEvent,
            )

            test_fs_input.file_system_observer._output_queue = None

            os.mkdir(os.path.join(new_dir_path, "bad_output_dir"))

            try:
                await self.process_dir_event_queue_response(
                    output_queue=output_queue,
                    dir_path=new_dir_path,
                    event_type=DirCreatedAtWatchLocationFSInputEvent,
                )
            except asyncio.exceptions.TimeoutError:
                pass

    @pytest.mark.asyncio
    async def test_DirTypeFSInput_bad_event_in_output_queue(
        self,
    ) -> None:
        """
        Unexpectedly set the input path to be None, and then monitor dir watcher.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            run_task, output_queue, test_fs_input = await self.get_DirTypeFSInput(
                new_dir_path
            )

            # There's no path, so there is currently no observer
            assert not hasattr(test_fs_input, "file_system_observer")

            # Create the dir - check for the response
            os.mkdir(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedAtWatchLocationFSInputEvent,
            )

            await test_fs_input.file_system_observer._internal_queue.put(None)

            run_task = asyncio.get_running_loop().create_task(
                test_fs_input.file_system_observer._process_event_from_watched_dir(event=None)
            )

            try:
                await self.cancel_task(run_task)
            except NotImplementedError:
                pass

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform.startswith("win"), reason="Linux (like) only test")
    async def testDirTypeFSInput_existing_dir_cre_del_dir_windows(self) -> None:
        """
        Check that we get the expected created signal from a dir created in a monitorbd dir
        Followed by an attempt to update the file.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            run_task, output_queue, _ = await self.get_DirTypeFSInput(tmp_dir_path)

            # - Using blocking methods - this should still work
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            os.mkdir(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedAtWatchLocationFSInputEvent,
            )

            shutil.rmtree(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=tmp_dir_path,
                event_type=DirUpdatedAtWatchLocationFSInputEvent,
            )
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirDeletedFromWatchLocationFSInputEvent,
            )

            await self.cancel_task(run_task)

    # @pytest.mark.asyncio
    # @pytest.mark.skipif(sys.platform.startswith("win"), reason="Linux (like) only test")
    # async def testDirTypeFSInput_existing_dir_cre_del_dir_loop_linux(self) -> None:
    #     """
    #     Checks we get the expected created signal from a file which is created in a monitored dir
    #     Followed by an attempt to update the file.
    #     Then an attempt to delete the file.
    #     This is done in a loop - to check for any problems with stale events
    #     """
    #     with tempfile.TemporaryDirectory() as tmp_dir_path:
    #         run_task, output_queue = await self.get_DirTypeFSInput(tmp_dir_path)
    #
    #         for i in range(10):
    #             # - Using blocking methods - this should still work
    #             new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me_txt")
    #
    #             os.mkdir(new_dir_path)
    #             if i == 0:
    #                 await self.process_dir_event_queue_response(
    #                     output_queue=output_queue,
    #                     dir_path=new_dir_path,
    #                     event_type=CreatedDirFSInputEvent,
    #                 )
    #
    #             else:
    #                 await self.process_dir_event_queue_response(
    #                     output_queue=output_queue,
    #                     dir_path=tmp_dir_path,
    #                     event_type=UpdatedDirFSInputEvent,
    #                 )
    #                 await self.process_dir_event_queue_response(
    #                     output_queue=output_queue,
    #                     dir_path=new_dir_path,
    #                     event_type=CreatedDirFSInputEvent,
    #                 )
    #
    #             shutil.rmtree(new_dir_path)
    #             await self.process_dir_event_queue_response(
    #                 output_queue=output_queue,
    #                 dir_path=tmp_dir_path,
    #                 event_type=UpdatedDirFSInputEvent,
    #             )
    #             await self.process_dir_event_queue_response(
    #                 output_queue=output_queue,
    #                 dir_path=new_dir_path,
    #                 event_type=DeletedDirFSInputEvent,
    #             )
    #
    #         await self.cancel_task(run_task)

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform.startswith("win"), reason="Linux (like) only test")
    async def testDirTypeFSInput_existing_dir_create_move_dir_linux(self) -> None:
        """
        Checks we get the expected created signal from a dir which is created in a monitored dir
        Followed by moving the dir.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            run_task, output_queue, _ = await self.get_DirTypeFSInput(tmp_dir_path)

            # - Using blocking methods - this should still work
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            os.mkdir(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedAtWatchLocationFSInputEvent,
            )

            await asyncio.sleep(0.1)

            # Move a file to a different location
            post_move_dir_path = os.path.join(tmp_dir_path, "moved_text_file_delete_me.txt")
            os.rename(src=new_dir_path, dst=post_move_dir_path)

            # This is an asymmetry between how files and folders handle delete
            # left in while I try and think how to deal sanely with it
            # await self.process_dir_deletion_response(output_queue, dir_path=new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=tmp_dir_path,
                event_type=DirMovedWithinWatchedDirFSInputEvent,
            )
            await self.process_file_move_queue_response(
                output_queue, file_src_parth=new_dir_path, file_dst_path=post_move_dir_path
            )

            await self.cancel_task(run_task)

    @pytest.mark.asyncio
    async def testDirTypeFSInput_existing_dir_create_move_dir(self) -> None:
        """
        Checks we get the expected created signal from a dir which is created in a monitored dir
        Followed by moving the dir.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            run_task, output_queue, _ = await self.get_DirTypeFSInput(tmp_dir_path)

            # - Using blocking methods - this should still work
            new_dir_path = os.path.join(tmp_dir_path, "text_file_delete_me.txt")

            os.mkdir(new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=new_dir_path,
                event_type=DirCreatedWithinWatchedDirFSInputEvent,
            )

            await asyncio.sleep(0.1)

            # Move a file to a different location
            post_move_dir_path = os.path.join(tmp_dir_path, "moved_text_file_delete_me.txt")
            os.rename(src=new_dir_path, dst=post_move_dir_path)

            # This is an asymmetry between how files and folders handle delete
            # left in while I try and think how to deal sanely with it
            # await self.process_dir_deletion_response(output_queue, dir_path=new_dir_path)
            await self.process_dir_event_queue_response(
                output_queue=output_queue,
                dir_path=tmp_dir_path,
                event_type=DirMovedWithinWatchedDirFSInputEvent,
            )

            # Now create a new folder inside the

            await self.cancel_task(run_task)

    # @pytest.mark.asyncio
    # @pytest.mark.skipif(sys.platform.startswith("win"), reason="Linux (like) only test")
    # async def testDirTypeFSInput_existing_dir_create_move_dir_loop_linux(self) -> None:
    #     """
    #     Checks we get the expected created signal from a dir which is created in a monitored dir
    #     Followed by moving the dir.
    #     Repeated in a loop.
    #     """
    #     with tempfile.TemporaryDirectory() as tmp_dir_path:
    #         new_subfolder_path = os.path.join(tmp_dir_path, "subfolder_1", "subfolder_2")
    #         os.makedirs(new_subfolder_path)
    #
    #         run_task, output_queue = await self.get_DirTypeFSInput(tmp_dir_path)
    #
    #         for i in range(10):
    #             # - Using blocking methods - this should still work
    #             new_dir_path = os.path.join(new_subfolder_path, "text_file_delete_me.txt")
    #
    #             os.mkdir(new_dir_path)
    #             if i == 0:
    #                 await self.process_dir_event_queue_response(
    #                     output_queue=output_queue,
    #                     dir_path=new_dir_path,
    #                     event_type=CreatedDirFSInputEvent,
    #                 )
    #             else:
    #                 await self.process_dir_event_queue_response(
    #                     output_queue=output_queue,
    #                     dir_path=new_dir_path,
    #                     event_type=CreatedDirFSInputEvent,
    #                 )
    #                 await self.process_dir_event_queue_response(
    #                     output_queue=output_queue,
    #                     dir_path=new_subfolder_path,
    #                     event_type=UpdatedDirFSInputEvent,
    #                 )
    #
    #             # Move a file to a different location
    #             post_move_dir_path = os.path.join(
    #                 new_subfolder_path, "moved_text_file_delete_me.txt"
    #             )
    #             os.rename(src=new_dir_path, dst=post_move_dir_path)
    #
    #             # I think this is a Windows problem - probably.
    #             if i == 0:
    #                 await self.process_dir_event_queue_response(
    #                     output_queue=output_queue,
    #                     dir_path=new_subfolder_path,
    #                     event_type=UpdatedDirFSInputEvent,
    #                 )
    #             await self.process_file_move_queue_response(
    #                 output_queue,
    #                 file_src_parth=new_dir_path,
    #                 file_dst_path=post_move_dir_path,
    #             )
    #             await self.process_dir_event_queue_response(
    #                 output_queue=output_queue,
    #                 dir_path=new_subfolder_path,
    #                 event_type=UpdatedDirFSInputEvent,
    #             )
    #
    #             shutil.rmtree(post_move_dir_path)
    #             await self.process_dir_event_queue_response(
    #                 output_queue=output_queue,
    #                 dir_path=post_move_dir_path,
    #                 event_type=DeletedDirFSInputEvent,
    #             )
    #             await self.process_dir_event_queue_response(
    #                 output_queue=output_queue,
    #                 dir_path=new_subfolder_path,
    #                 event_type=UpdatedDirFSInputEvent,
    #             )
    #
    #         await self.cancel_task(run_task)
