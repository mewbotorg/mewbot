#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Provides an IOConfig which listens on a host-socket combination for traffic.

If data is received, will acknowledge and generate an InputEvent containing it.
"""

from __future__ import annotations

from typing import Optional, Sequence, Set, Type

import asyncio
import dataclasses
import logging
import time

from mewbot.api.v1 import Input, InputEvent, IOConfig, Output


@dataclasses.dataclass
class SocketInputEvent(InputEvent):
    """
    Event generated when data is sent to a monitored socket.
    """

    data: bytes


class SocketIO(IOConfig):
    """
    IOConfig which supports receiving data sent to a socket.
    """

    _host: str = "localhost"
    _port: int = 0

    _logger: logging.Logger

    _socket: Optional[SocketInput]

    def __init__(self) -> None:
        """
        Initialise the SocketIO IOConfig.
        """
        self._logger = logging.getLogger(__name__ + "SocketInput")
        self._socket = None

    @property
    def host(self) -> str:
        """
        Returns the host this IOConfig will listen on.

        The port this IOConfig will listen is given by :meth port:.
        :return:
        """
        return self._host

    @host.setter
    def host(self, host: str) -> None:
        self._host = str(host)

    @property
    def port(self) -> int:
        """
        Returns the port this IOConfig will listen on.
        """
        return self._port

    @port.setter
    def port(self, port: int) -> None:
        self._port = int(port)

    def _create_socket(self) -> SocketInput:
        return SocketInput(self._host, self._port, self._logger)

    def get_inputs(self) -> Sequence[Input]:
        """
        Returns the inputs for SocketIO.

        There should be one - a listener which listens to a port on a host.
        All data sent to that port on the host will be put on the wire.
        :return:
        """
        if not self._socket:
            self._socket = self._create_socket()

        return [self._socket]

    def get_outputs(self) -> Sequence[Output]:
        """
        Gets the Outputs for the SocketIO class.

        In this case, there shouldn't be any, because output is not supported.
        """
        return []


class SocketInput(Input):
    """
    Listens to a socket for data which will then be put on the wire.

    Not complete, but it took an annoyingly long time to get working.
    so I'm leaving it in for future use.
    """

    _logger: logging.Logger

    _socket: Optional[asyncio.AbstractServer]

    _host: str
    _port: int

    def __init__(self, host: str, port: int, logger: logging.Logger) -> None:
        """
        Initialize a SocketInput.

        This class still needs to be run.
        :param host: Host the socket is on
        :param port: Port for the socket
        :param logger: logging.Logger logger for logging.
        """
        super().__init__()

        self._logger = logger
        self._socket = None
        self._host = host
        self._port = port

    @staticmethod
    def produces_inputs() -> Set[Type[InputEvent]]:
        """
        Defines the set of input events this Input class can produce.
        """
        return {SocketInputEvent}

    async def run(self) -> None:
        """
        Receive input from the socket we're listening to.
        """
        if not self.queue:
            self._logger.error(".run() called before queue bound")
            return
        if self._socket:
            self._logger.error(".run() called with existing socket")
            return

        self._logger.info("Binding get server to %s:%d", self._host, self._port)

        self._socket = await asyncio.start_server(self.handle_client, self._host, self._port)

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """
        Handles connections from a client.

         - accept a connection from a client.
         - read the incoming data.
         - put it on the wire in the form of an OutputEvent
        - write a confirmation message noting receipt to the original host.
        :param reader:
        :param writer:
        :return:
        """
        self._logger.info("Accepting connection from %s", reader)

        while not reader.at_eof():
            try:
                data = await asyncio.wait_for(reader.readline(), 15)
            except asyncio.TimeoutError:
                writer.write(b"Timeout waiting for message\n")
                break

            if not self.queue:
                self._logger.warning("Received event with no attached queue")
                writer.write(b"No queue attached, aborting.\n")
                break

            await self.queue.put(SocketInputEvent(data=data))
            writer.write(
                b"Accepted event of "
                + hex(len(data)).encode("utf-8")
                + b" bytes at "
                + str(time.time()).encode("utf-8")
                + b"\r\n"
            )

        writer.write_eof()
        writer.close()
