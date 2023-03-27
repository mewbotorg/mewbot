# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Set of basic tools to improve command line readability.
"""

import shutil
from types import TracebackType

from typing import Optional


class CommandDeliminator:
    """Used to more cleanly separate one command in a run from another."""

    tool_name: Optional[str]
    delin_char: str

    def __init__(self, tool_name: Optional[str] = None, delin_char: str = "-") -> None:
        """
        Supplied with the name of the tool and the deliminator char to create a display.

        :param delin_char:
        :param tool_name:
        """
        self.tool_name = tool_name
        self.delin_char = delin_char

    @property
    def terminal_width(self) -> int:
        """
        Recalculated live in case the terminal changes sizes between calls.

        Falls back to 80.
        :return: int terminal width
        """
        return shutil.get_terminal_size((80, 20))[0]

    def __enter__(self) -> None:
        """
        Print the welcome message.

        :return:
        """

        print("#" + self.delin_char * (self.terminal_width - 2))
        if self.tool_name is not None:
            print(self.tool_name + "\n")

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """
        Print the exit message.

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        # https://stackoverflow.com/questions/18398672/re-raising-an-exception-in-a-context-handler
        if exc_type:
            return False

        print("#\n" + "#" + self.delin_char * (self.terminal_width - 2))

        return True
