# Unified test of http and socket parts of mewbot.io
# Loads a file in, sees if it works, and then probes the socket and http class.

from __future__ import annotations

from typing import Type

import asyncio
import copy
import logging
import socket

import pytest

from mewbot_tests.common import BaseTestClassWithConfig

from mewbot.io.http import HTTPServlet
from mewbot.io.socket import SocketIO, SocketInput
from mewbot.api.v1 import IOConfig
from mewbot.core import InputQueue

# pylint: disable=R0903
#  Disable "too few public methods" for test cases - most test files will be classes used for
#  grouping and then individual tests alongside these


class TestIoHttpsPost(BaseTestClassWithConfig[HTTPServlet]):
    config_file: str = "examples/trivial_http_post.yaml"
    implementation: Type[HTTPServlet] = HTTPServlet

    def test_check_class(self) -> None:
        assert isinstance(self.component, HTTPServlet)
        assert isinstance(self.component, SocketIO)
        assert isinstance(self.component, IOConfig)

    def test_check_setget(self) -> None:
        # Check each set and get
        temp_component = copy.deepcopy(self.component)

        new_host = "nullfailtouse"
        temp_component.host = new_host
        assert temp_component.host == new_host

        new_port = 0
        temp_component.port = new_port
        assert temp_component.port == new_port

    @pytest.mark.asyncio
    async def test_component_http_socket_run(self) -> None:
        """
        Run the component's input method - should run without throwing an error.
        """
        component_http_socket_input = self.component.get_inputs()
        assert isinstance(component_http_socket_input, list)
        assert len(component_http_socket_input) == 1

        test_http_io_input = component_http_socket_input[0]

        # Run the input
        try:
            await asyncio.wait_for(test_http_io_input.run(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_direct_socket_input_run_no_queue(self) -> None:
        """
        Load and directly run the socket input
        :return:
        """
        test_input = SocketInput(
            host="localhost", port=56789, logger=logging.getLogger(__name__ + "SocketInput")
        )

        try:
            await asyncio.wait_for(test_input.run(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_direct_socket_input_run(self) -> None:
        """
        Load and directly run the socket input - after binding in a queue.
        :return:
        """
        test_input = SocketInput(
            host="localhost", port=56789, logger=logging.getLogger(__name__ + "SocketInput")
        )

        test_input_queue = InputQueue()
        test_input.bind(test_input_queue)

        try:
            await asyncio.wait_for(test_input.run(), 1)
        except asyncio.exceptions.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_direct_socket_input_start_server_with_handle_client(self) -> None:
        """
        Start a server with handle_client from the input
        :return:
        """
        # Need access to protected members to enable full testing
        # pylint: disable=W0212

        test_input = SocketInput(
            host="localhost", port=56789, logger=logging.getLogger(__name__ + "SocketInput")
        )

        test_input_queue = InputQueue()
        test_input.bind(test_input_queue)

        try:
            await asyncio.wait_for(
                asyncio.start_server(
                    test_input.handle_client, test_input._host, test_input._port
                ),
                1,
            )
        except asyncio.exceptions.TimeoutError:
            pass

    # @pytest.mark.asyncio
    # async def test_direct_socket_input_start_server_handle_client_directly_called(self) -> None:
    #     """
    #     Directly call handle client.
    #     :return:
    #     """
    #     test_input = SocketInput(
    #         host="localhost", port=56789, logger=logging.getLogger(__name__ + "SocketInput")
    #     )
    #
    #     test_input_queue = InputQueue()
    #     test_input.bind(test_input_queue)
    #
    #     input_stream = asyncio.StreamReader()
    #     output_stream = asyncio.StreamWriter()
    #

    async def ping_socket(self, wait: float = 0.5) -> None:
        """
        Wait a period of time and then write some data to the component's port.
        :return:
        """
        await asyncio.sleep(wait)

        target_socket = socket.socket()
        target_socket.connect((self.component.host, self.component.port))

        target_socket.send("Test data".encode())
