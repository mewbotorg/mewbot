import asyncio

from typing import Tuple, Optional, List, Union, Type

from mewbot.api.v1 import InputEvent
from mewbot.io.file_system import (
    DirTypeFSInput,
    FileTypeFSInput,
)
from mewbot.io.file_system.events import (
    InputFileFileCreationInputEvent,
    InputFileFileDeletionInputEvent,
    InputFileDirCreationInputEvent,
    FileFSInputEvent,
    CreatedFileFSInputEvent,
    UpdatedFileFSInputEvent,
    MovedFileFSInputEvent,
    DeletedFileFSInputEvent,
    DirFSInputEvent,
    CreatedDirFSInputEvent,
    MovedDirFSInputEvent,
    UpdatedDirFSInputEvent,
    DeletedDirFSInputEvent,
)


# pylint: disable=invalid-name
# for clarity, factory functions should be named after the things they test


class GeneralUtils:
    @staticmethod
    async def _get_worker(
        output_queue: asyncio.Queue[InputEvent], rtn_event: List[InputEvent]
    ) -> None:
        rtn_event.append(await output_queue.get())

    async def timeout_get(
        self, output_queue: asyncio.Queue[InputEvent], timeout: float = 20.0
    ) -> InputEvent:

        rtn_event: List[InputEvent] = []
        await asyncio.wait_for(self._get_worker(output_queue, rtn_event), timeout=timeout)
        if len(rtn_event) == 1:
            return rtn_event[0]
        if len(rtn_event) == 0:
            raise asyncio.QueueEmpty
        raise NotImplementedError(f"Unexpected case {rtn_event}")

    @staticmethod
    def dump_queue_to_list(output_queue: asyncio.Queue[InputEvent]) -> List[InputEvent]:
        """
        Take a queue - extract all the entries and return them as a list.
        """
        input_events = []
        while True:
            try:
                input_events.append(output_queue.get_nowait())
            except asyncio.QueueEmpty:
                break

        return input_events

    @staticmethod
    async def get_DirTypeFSInput(
        input_path: str,
    ) -> Tuple[asyncio.Task[None], asyncio.Queue[InputEvent]]:

        test_fs_input = DirTypeFSInput(input_path=input_path)
        assert isinstance(test_fs_input, DirTypeFSInput)

        output_queue: asyncio.Queue[InputEvent] = asyncio.Queue()
        test_fs_input.queue = output_queue

        # We need to retain control of the thread to delay shutdown
        # And to probe the results
        run_task = asyncio.get_running_loop().create_task(test_fs_input.run())

        # Give the class a chance to actually do init
        await asyncio.sleep(0.5)

        return run_task, output_queue

    @staticmethod
    async def get_FileTypeFSInput(
        input_path: str,
    ) -> Tuple[asyncio.Task[None], asyncio.Queue[InputEvent]]:

        test_fs_input = FileTypeFSInput(input_path=input_path)
        assert isinstance(test_fs_input, FileTypeFSInput)

        output_queue: asyncio.Queue[InputEvent] = asyncio.Queue()
        test_fs_input.queue = output_queue

        # We need to retain control of the thread to delay shutdown
        # And to probe the results
        run_task = asyncio.get_running_loop().create_task(test_fs_input.run())

        return run_task, output_queue

    @staticmethod
    async def cancel_task(run_task: asyncio.Task[None]) -> None:

        # Otherwise the queue seems to be blocking pytest from a clean exit.
        try:
            run_task.cancel()
            await run_task
        except asyncio.exceptions.CancelledError:
            pass

    @staticmethod
    async def verify_queue_size(
        output_queue: asyncio.Queue[InputEvent],
        task_done: bool = True,
        allowed_queue_size: int = 0,
    ) -> None:
        # There should be no other events in the queue
        output_queue_qsize = output_queue.qsize()
        if allowed_queue_size:
            assert output_queue_qsize in (0, allowed_queue_size), (
                f"Output queue actually has {output_queue_qsize} entries "
                f"- the allowed_queue_size is either {allowed_queue_size} or zero"
            )
        else:
            assert output_queue_qsize == 0, (
                f"Output queue actually has {output_queue_qsize} entries "
                f"- None are allowed"
            )

        # Indicate to the queue that task processing is complete
        if task_done:
            output_queue.task_done()


class FileSystemTestUtilsFileEvents(GeneralUtils):
    async def process_file_event_queue_response(
        self,
        output_queue: asyncio.Queue[InputEvent],
        event_type: Union[
            Type[FileFSInputEvent],
            Type[InputFileFileCreationInputEvent],
            Type[InputFileFileDeletionInputEvent],
        ],
        file_path: Optional[str] = None,
        allowed_queue_size: int = 0,
    ) -> None:
        """
        Get the next event off the queue.
        Check that it's one for a file being created with expected file path.
        """

        # This should have generated an event
        queue_out = await self.timeout_get(output_queue)
        self.validate_file_input_event(
            input_event=queue_out, event_type=event_type, file_path=file_path
        )

        await self.verify_queue_size(output_queue, allowed_queue_size=allowed_queue_size)

    def check_queue_for_file_input_event(
        self,
        output_queue: Union[asyncio.Queue[InputEvent], List[InputEvent]],
        event_type: Type[FileFSInputEvent],
        file_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        if isinstance(output_queue, asyncio.Queue):
            input_events = self.dump_queue_to_list(output_queue)
        elif isinstance(output_queue, list):
            input_events = output_queue
        else:
            raise NotImplementedError(f"{output_queue} of unsupported type")

        for event in input_events:
            if isinstance(event, event_type):
                self.validate_file_input_event(
                    input_event=event,
                    event_type=event_type,
                    file_path=file_path,
                    message=message,
                )
                return

        raise AssertionError(
            f"CreatedFileFSInputEvent not found in input_events - {input_events}"
        )

    @staticmethod
    def validate_file_input_event(
        input_event: InputEvent,
        event_type: Union[
            Type[FileFSInputEvent],
            Type[InputFileFileCreationInputEvent],
            Type[InputFileFileDeletionInputEvent],
        ],
        file_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        assert isinstance(
            input_event, event_type
        ), f"Expected event of type {event_type.__name__} - got {input_event}" + (
            f" - {message}" if message else ""
        )

        if file_path is not None:
            assert isinstance(
                input_event,
                (
                    FileFSInputEvent,
                    InputFileFileCreationInputEvent,
                    InputFileFileDeletionInputEvent,
                ),
            )
            assert input_event.file_path == file_path

    def check_queue_for_file_creation_input_event(
        self,
        output_queue: Union[asyncio.Queue[InputEvent], List[InputEvent]],
        file_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        """
        Check the given queue to see that there is a CreatedFileFSInputEvent in it.
        """
        if isinstance(output_queue, asyncio.Queue):
            input_events = self.dump_queue_to_list(output_queue)
        elif isinstance(output_queue, list):
            input_events = output_queue
        else:
            raise NotImplementedError(f"{output_queue} of unsupported type")

        for event in input_events:
            if isinstance(event, CreatedFileFSInputEvent):
                self.validate_file_creation_input_event(
                    input_event=event, file_path=file_path, message=message
                )
                return

        raise AssertionError(
            f"CreatedFileFSInputEvent not found in input_events - {input_events}"
        )

    @staticmethod
    def validate_file_creation_input_event(
        input_event: InputEvent,
        file_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        assert isinstance(
            input_event, CreatedFileFSInputEvent
        ), f"Expected CreatedFileFSInputEvent - got {input_event}" + (
            f" - {message}" if message else ""
        )

        if file_path is not None:
            assert input_event.file_path == file_path

    def check_queue_for_file_update_input_event(
        self,
        output_queue: Union[asyncio.Queue[InputEvent], List[InputEvent]],
        file_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        """
        Check the given queue to see that there is a CreatedFileFSInputEvent in it.
        """
        if isinstance(output_queue, asyncio.Queue):
            input_events = self.dump_queue_to_list(output_queue)
        elif isinstance(output_queue, list):
            input_events = output_queue
        else:
            raise NotImplementedError(f"{output_queue} of unsupported type")

        for event in input_events:
            if isinstance(event, UpdatedFileFSInputEvent):
                self.validate_file_update_input_event(
                    input_event=event, file_path=file_path, message=message
                )
                return

        raise AssertionError(
            f"UpdatedFileFSInputEvent not found in input_events - {input_events}"
        )

    @staticmethod
    def validate_file_update_input_event(
        input_event: InputEvent,
        file_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        assert isinstance(
            input_event, UpdatedFileFSInputEvent
        ), f"Expected UpdatedFileFSInputEvent - got {input_event}" + (
            f" - {message}" if message else ""
        )

        if file_path is not None:
            assert file_path == input_event.file_path

    def check_queue_for_file_move_input_event(
        self,
        output_queue: Union[asyncio.Queue[InputEvent], List[InputEvent]],
        file_src_parth: Optional[str] = None,
        file_dst_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        """
        Check the given queue to see that there is a CreatedFileFSInputEvent in it.
        """
        if isinstance(output_queue, asyncio.Queue):
            input_events = self.dump_queue_to_list(output_queue)
        elif isinstance(output_queue, list):
            input_events = output_queue
        else:
            raise NotImplementedError(f"{output_queue} of unsupported type")

        for event in input_events:
            if isinstance(event, MovedFileFSInputEvent):
                self.validate_file_move_input_event(
                    input_event=event,
                    file_src_parth=file_src_parth,
                    file_dst_path=file_dst_path,
                    message=message,
                )
                return

        raise AssertionError(
            f"UpdatedDirFSInputEvent not found in input_events - {input_events}"
        )

    async def process_file_move_queue_response(
        self,
        output_queue: asyncio.Queue[InputEvent],
        file_src_parth: Optional[str] = None,
        file_dst_path: Optional[str] = None,
        allowed_queue_size: int = 0,
    ) -> None:
        """
        Get the next event off the queue - check that it's one for the input file being deleted.
        """
        # This should have generated an event
        queue_out = await self.timeout_get(output_queue)
        self.validate_file_move_input_event(
            input_event=queue_out,
            file_src_parth=file_src_parth,
            file_dst_path=file_dst_path,
        )

        await self.verify_queue_size(output_queue, allowed_queue_size=allowed_queue_size)

    @staticmethod
    def validate_file_move_input_event(
        input_event: InputEvent,
        file_src_parth: Optional[str] = None,
        file_dst_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        assert isinstance(
            input_event, MovedFileFSInputEvent
        ), f"Expected MovedFileFSInputEvent - got {input_event}" + (
            f" - {message}" if message else ""
        )

        if file_src_parth is not None:
            assert input_event.file_src == file_src_parth

        if file_dst_path is not None:
            assert input_event.file_path == file_dst_path

    def check_queue_for_file_deletion_input_event(
        self,
        output_queue: Union[asyncio.Queue[InputEvent], List[InputEvent]],
        file_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        """
        Check the given queue to see that there is a CreatedFileFSInputEvent in it.
        """
        if isinstance(output_queue, asyncio.Queue):
            input_events = self.dump_queue_to_list(output_queue)
        elif isinstance(output_queue, list):
            input_events = output_queue
        else:
            raise NotImplementedError(f"{output_queue} of unsupported type")

        for event in input_events:
            if isinstance(event, DeletedFileFSInputEvent):
                self.validate_file_deletion_input_event(
                    input_event=event, file_path=file_path, message=message
                )
                return

        raise AssertionError(
            f"DeletedFileFSInputEvent not found in input_events - {input_events}"
        )

    @staticmethod
    def validate_file_deletion_input_event(
        input_event: InputEvent,
        file_path: Optional[str] = None,
        message: str = "",
    ) -> None:

        if file_path is not None:
            assert isinstance(
                input_event, DeletedFileFSInputEvent
            ), f"expected DeletedFileFSInputEvent - got {input_event}" + (
                f" - {message}" if message else ""
            )
            assert file_path == input_event.file_path, (
                f"file path does not match expected - wanted {file_path}, "
                f"got {input_event.file_path}"
            )
        else:
            assert isinstance(
                input_event, DeletedFileFSInputEvent
            ), f"expected DeletedFileFSInputEvent - got {input_event}" + (
                f" - {message}" if message else ""
            )


class FileSystemTestUtilsDirEvents(GeneralUtils):
    async def process_dir_event_queue_response(
        self,
        output_queue: asyncio.Queue[InputEvent],
        event_type: Type[DirFSInputEvent],
        dir_path: Optional[str] = None,
        allowed_queue_size: int = 1,
    ) -> None:
        """
        Get the next event off the queue.
        Check that it's one for a file being created with expected file path.
        """

        # This should have generated an event
        queue_out = await self.timeout_get(output_queue)
        self.validate_dir_input_event(
            input_event=queue_out, event_type=event_type, dir_path=dir_path
        )

        await self.verify_queue_size(output_queue, allowed_queue_size=allowed_queue_size)

    def check_queue_for_dir_input_event(
        self,
        output_queue: Union[asyncio.Queue[InputEvent], List[InputEvent]],
        event_type: Type[DirFSInputEvent],
        dir_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        if isinstance(output_queue, asyncio.Queue):
            input_events = self.dump_queue_to_list(output_queue)
        elif isinstance(output_queue, list):
            input_events = output_queue
        else:
            raise NotImplementedError(f"{output_queue} of unsupported type")

        for event in input_events:
            if isinstance(event, event_type):
                self.validate_dir_input_event(
                    input_event=event,
                    event_type=event_type,
                    dir_path=dir_path,
                    message=message,
                )
                return

        raise AssertionError(
            f"CreatedFileFSInputEvent not found in input_events - {input_events}"
        )

    @staticmethod
    def validate_dir_input_event(
        input_event: InputEvent,
        event_type: Type[DirFSInputEvent],
        dir_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        assert isinstance(
            input_event, event_type
        ), f"Expected event of type {event_type.__name__} - got {input_event}" + (
            f" - {message}" if message else ""
        )

        if dir_path is not None:
            assert (
                input_event.dir_path == dir_path
            ), f"expected {dir_path}, got {input_event.dir_path}"

    @staticmethod
    def validate_dir_creation_input_event(
        input_event: InputEvent,
        dir_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        assert isinstance(
            input_event, CreatedDirFSInputEvent
        ), f"Expected CreatedDirFSInputEvent - got {input_event}" + (
            f" - {message}" if message else ""
        )
        if dir_path is not None:
            assert input_event.dir_path == dir_path

    def check_queue_for_dir_update_input_event(
        self,
        output_queue: Union[asyncio.Queue[InputEvent], List[InputEvent]],
        dir_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        """
        Check the given queue to see that there is a CreatedFileFSInputEvent in it.
        """
        if isinstance(output_queue, asyncio.Queue):
            input_events = self.dump_queue_to_list(output_queue)
        elif isinstance(output_queue, list):
            input_events = output_queue
        else:
            raise NotImplementedError(f"{output_queue} of unsupported type")

        for event in input_events:
            if isinstance(event, UpdatedDirFSInputEvent):
                self.validate_dir_update_input_event(
                    input_event=event, dir_path=dir_path, message=message
                )
                return

        raise AssertionError(
            f"UpdatedDirFSInputEvent not found in input_events - {input_events}"
        )

    @staticmethod
    def validate_dir_update_input_event(
        input_event: InputEvent,
        dir_path: Optional[str] = None,
        message: str = "",
    ) -> None:

        err_str = f"Expected UpdatedDirFSInputEvent - got {input_event}" + (
            f" - {message}" if message else ""
        )
        assert isinstance(input_event, UpdatedDirFSInputEvent), err_str

        if dir_path is not None:
            assert (
                input_event.dir_path == dir_path
            ), f"expected {dir_path} - got {input_event.dir_path}"

    async def process_input_file_creation_response(
        self, output_queue: asyncio.Queue[InputEvent], file_path: str = "", message: str = ""
    ) -> None:
        """
        This event is emitted when we're in file mode, monitoring a file, which does not yet exist.
        When the file is created, this event is emitted.
        """

        # This should have generated an event
        queue_out = await self.timeout_get(output_queue)
        self.validate_input_file_creation_input_event(
            input_event=queue_out, file_path=file_path, message=message
        )

        await self.verify_queue_size(output_queue)

    @staticmethod
    def validate_input_file_creation_input_event(
        input_event: InputEvent,
        file_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        assert isinstance(input_event, InputFileFileCreationInputEvent)
        if file_path:
            err_str = f"Expected UpdatedDirFSInputEvent - got {input_event}" + (
                f" - {message}" if message else ""
            )
            assert input_event.file_path == file_path, err_str

    @staticmethod
    def validate_input_dir_creation_input_event(
        input_event: InputEvent,
        dir_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        assert isinstance(
            input_event, InputFileDirCreationInputEvent
        ), f"Expected InputFileDirCreationInputEvent - got {input_event}" + (
            f" - {message}" if message else ""
        )
        if dir_path:
            assert input_event.dir_path == dir_path, (
                f"dir_path is not as expected - theo - {dir_path} - "
                f"actual {input_event.dir_path}" + (message if message else "")
            )

    async def process_dir_move_queue_response(
        self,
        output_queue: asyncio.Queue[InputEvent],
        dir_src_parth: Optional[str] = None,
        dir_dst_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        """
        Get the next event off the queue - check that it's one for the input file being deleted.
        """
        # This should have generated an event
        queue_out = await self.timeout_get(output_queue)
        self.validate_dir_move_input_event(
            input_event=queue_out,
            dir_src_parth=dir_src_parth,
            dir_dst_path=dir_dst_path,
            message=message,
        )

        await self.verify_queue_size(output_queue)

    @staticmethod
    def validate_dir_move_input_event(
        input_event: InputEvent,
        dir_src_parth: Optional[str] = None,
        dir_dst_path: Optional[str] = None,
        message: str = "",
    ) -> None:
        assert isinstance(
            input_event, MovedDirFSInputEvent
        ), f"Expected MovedDirFSInputEvent - got {input_event}" + (
            f" - {message}" if message else ""
        )

        if dir_src_parth is not None:
            assert input_event.dir_path == dir_src_parth

        if dir_dst_path is not None:
            assert input_event.dir_src_path == dir_dst_path

    @staticmethod
    def validate_dir_deletion_input_event(
        input_event: InputEvent,
        dir_path: Optional[str] = None,
        message: str = "",
    ) -> None:

        assert isinstance(
            input_event, DeletedDirFSInputEvent
        ), f"Expected DeletedDirFSInputEvent - got {input_event}" + (
            f" - {message}" if message else ""
        )

        if dir_path is not None:
            assert input_event.dir_path == dir_path

    @staticmethod
    def validate_input_file_deletion_input_event(
        input_event: InputEvent,
        file_path: str = "",
        message: str = "",
    ) -> None:
        assert isinstance(
            input_event, InputFileFileDeletionInputEvent
        ), f"Expected DeletedDirFSInputEvent - got {input_event}" + (
            f" - {message}" if message else ""
        )
        if file_path:
            assert (
                input_event.file_path == file_path
            ), f"File path was not as expected - expected {file_path} - got {input_event.file_path}"
