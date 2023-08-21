"""
Allows you to generate InputEvents and receive OutputEvents via typing in the shell.

Mostly used for demo purposes.
"""


from typing import Iterable

import asyncio
import os
import sys

from mewbot.api.v1 import Input, InputEvent, IOConfig, Output, OutputEvent
from mewbot.io.common import EventWithReplyMixIn


class StandardConsoleInputOutput(IOConfig):
    """
    Prints to shell and reads things type in it back.
    """

    def get_inputs(self) -> Iterable[Input]:
        """
        Input will read from stdio.

        :return:
        """
        return [StandardInput()]

    def get_outputs(self) -> Iterable[Output]:
        """
        Output will print to the console.

        :return:
        """
        return [StandardOutput()]


class ConsoleInputLine(EventWithReplyMixIn):
    """
    Input event generated when the user types a line in the console.
    """

    message: str

    def __init__(self, message: str) -> None:
        """
        Startup with the line drawn from the console.

        :param message:
        """
        self.message = message

    def __str__(self) -> str:
        """
        Str rep of this event.

        :return:
        """
        return f"ConsoleInputLine: \"{self.message}\""

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


class ConsoleOutputLine(OutputEvent):  # pylint:disable=too-few-public-methods
    """
    Line to be printer to the console.
    """

    message: str

    def __init__(self, message: str) -> None:
        """
        Takes the console output line as a string.

        :param message:
        """
        self.message = message

    def __str__(self) -> str:
        """
        Str representation of the original message.

        :return:
        """
        return self.message


class StandardInput(Input):
    """
    Reads lines from the console ever time the user enters one.
    """

    @staticmethod
    def produces_inputs() -> set[type[InputEvent]]:
        """
        Produces ConsoleInputLine InputEvents.

        :return:
        """
        return {ConsoleInputLine}

    @staticmethod
    async def connect_stdin_stdout() -> asyncio.StreamReader:
        """
        Async compatible - non-blocking - console line reader.

        :return:
        """
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        return reader

    async def run(self) -> None:
        """
        Process input typed at the console and convert it to InputEvents on the wire.

        :return:
        """
        if os.name.lower() != "nt":
            await self._linux_run()
        else:
            await self._windows_run()

    async def _linux_run(self) -> None:
        """
        Linux version of the async reader.

        :return:
        """
        reader = await self.connect_stdin_stdout()
        while line := await reader.readline():
            if self.queue:
                await self.queue.put(ConsoleInputLine(line.decode()))

    async def _windows_run(self) -> None:
        """
        Windows version of the async reader.

        :return:
        """
        while line := await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline):
            if self.queue:
                await self.queue.put(ConsoleInputLine(line))


class StandardOutput(Output):
    """
    Write out to the console.
    """

    @staticmethod
    def consumes_outputs() -> set[type[OutputEvent]]:
        """
        Takes lines to write out to the active console.

        :return:
        """
        return {ConsoleOutputLine}

    async def output(self, event: OutputEvent) -> bool:
        """
        Just uses the print command to write out to the console.

        :param event:
        :return:
        """
        print(event)
        return True
