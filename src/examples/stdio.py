from typing import Iterable

import asyncio
import os
import sys

from mewbot.api.v1 import Input, InputEvent, IOConfig, Output, OutputEvent
from mewbot.io.common import EventWithReplyMixIn


class StandardConsoleInputOutput(IOConfig):
    def get_inputs(self) -> Iterable[Input]:
        return [StandardInput()]

    def get_outputs(self) -> Iterable[Output]:
        return [StandardOutput()]


class ConsoleInputLine(EventWithReplyMixIn):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message

    def get_sender_name(self) -> str:
        """
        Returns the human friend name/nickname of the user who sent the event.
        """
        return os.getlogin()

    def get_sender_mention(self) -> str:
        """
        Returns the string contents required to mention/notify/ping the sender.

        If the reply methods will automatically ping the user, this may just be
        the human-readable username.
        """
        return os.getlogin()

    def prepare_reply(self, message: str) -> OutputEvent:
        """
        Creates an OutputEvent which is a reply to this input event.

        This event will be targeted at the same scope as the incoming message,
        e.g. in the same channel. It is expected that all people who saw the
        original message will also be able to see the reply.
        """
        return ConsoleOutputLine(message)

    def prepare_reply_narrowest_scope(self, message: str) -> OutputEvent:
        """
        Creates an OutputEvent which is a reply to this input event.

        This event will attempt to only be visible to a minimal number of
        people which still includes the person who sent the message.
        Note that for some systems, this may still be the original scope
        of all users who could see the original message.

        This function does not guarantee privacy, but is intended for use
        where replies are not relevant to other users, and thus can clutter
        up the main chat.
        """
        return ConsoleOutputLine(message)


class ConsoleOutputLine(OutputEvent):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class StandardInput(Input):
    @staticmethod
    def produces_inputs() -> set[type[InputEvent]]:
        return {ConsoleInputLine}

    @staticmethod
    async def connect_stdin_stdout() -> asyncio.StreamReader:
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        return reader

    async def run(self) -> None:
        reader = await self.connect_stdin_stdout()
        while line := await reader.readline():
            if self.queue:
                await self.queue.put(ConsoleInputLine(line.decode()))


class StandardOutput(Output):
    @staticmethod
    def consumes_outputs() -> set[type[OutputEvent]]:
        return {ConsoleOutputLine}

    async def output(self, event: OutputEvent) -> bool:
        print(event)
        return True
