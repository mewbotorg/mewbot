# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Set of basic tools to improve command line readability.
"""

import shutil
from types import TracebackType

from typing import Optional

from clint.textui import colored  # type: ignore


class CommandDeliminator:
    """Used to more cleanly separate one command in a run from another."""

    tool_name: Optional[str]
    delin_char: str

    def __init__(self, tool_name: Optional[str] = None, delin_char: str = "-") -> None:
        """
        Supplied with the name of the tool and the deliminator char to create a display.

        :param delin_char: This will fill the line below and above the tool run
        :param tool_name: The name of the tool which will be run
        """
        self.tool_name = tool_name
        self.delin_char = delin_char

    @property
    def terminal_width(self) -> int:
        """
        Recalculated live in case the terminal changes sizes between calls.

        Fallback is to assume 8 char wide - which seems a reasonable minimum for terminal size.
        :return: int terminal width
        """
        return shutil.get_terminal_size((80, 20))[0]

    def __enter__(self) -> None:
        """Print the welcome message."""

        print("#" + self.delin_char * (self.terminal_width - 2))
        if self.tool_name is not None:
            print(self.tool_name + "\n")

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """Print the exit message."""
        # https://stackoverflow.com/questions/18398672/re-raising-an-exception-in-a-context-handler
        if exc_type:
            return False

        print("#\n" + "#" + self.delin_char * (self.terminal_width - 2))

        return True


class ResultPrinter:
    """Formats the given results dicsts into a final output string."""

    results: dict[str, bool]

    def __init__(self, *results: dict[str, bool]) -> None:
        """
        Load the class with dicts to print.

        Keyed with the name of the run and valued with its status.
        """
        self.results = {}

        for result in results:
            self.results.update(result)

    def result_print(self) -> None:
        """Print the collected results."""
        result_strs: list[str] = []

        can_upload: bool = True
        for run_name, run_status in self.results.items():
            if can_upload and not run_status:
                can_upload = False
            result_strs.append(self.format_result_str(run_name, run_status))

        print(
            "\n".join(result_strs)
            + f"\nCongratulations! {colored.green('Proceed to Upload')}"
            if can_upload
            else "\n".join(result_strs)
            + f"\nBad news! {colored.red('At least one failure!')}"
        )

    @staticmethod
    def format_result_str(proc_name: str, proc_status: bool) -> str:
        """Get a formatted string for an individual result."""
        return f"{proc_name}: [{colored.green('Yes') if proc_status else colored.red('No')}]"
