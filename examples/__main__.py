#!/usr/bin/env python3

# There are two ways this can be run
# - if you pass the path of a mewbot yaml configuration to this script it will be run
# - if you pass no paths in, you get an interactive view from which you can select what to be run
# - - this allows you to run examples which are declared by mewbot plugins installed on the system
# - - these will be included as virtual folders in the examples dir

from __future__ import annotations

from typing import Tuple, List, Dict

import os
import sys

import mewbot.loader
from mewbot.plugins.hook_specs import gather_dev_paths


class NoArgsMainRunner:
    """
    Represents all the found examples, and the user's interaction with them.
    """

    # Any yaml file names which should not be offered as options to the user
    YAML_FILTER_LIST: Tuple[str] = ("examples_to_filter_go_here.yaml",)

    num_path_map: Dict[int, str] = {}

    target_bot: str = ""

    def __init__(self) -> None:
        """
        Startup the session.
        """
        # Gather the additional paths which should be included at the top level of examples
        example_dirs = gather_dev_paths("declare_example_locs")
        self.example_dirs = self.good_sort_example_dirs(example_dirs)

        # Display the available paths and also assign the paths to numbers
        self.list_files(startpaths=self.example_dirs)

        # Ask the user for the bot they want to run
        self.prompt_user()

        # Run the bot
        self.run_bot()

    @staticmethod
    def good_sort_example_dirs(example_dirs: List[str]) -> List[str]:
        """
        Sort the declared directories.
        :param example_dirs:
        :return:
        """
        return sorted(example_dirs, key=lambda x: os.path.split(x)[1])

    def list_files(self, startpaths: List[str]) -> None:
        """
        From https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
        Will also assign the paths to numbers
        :param startpaths: Path tp start the recursion from - should be "examples"
                           (Or something similar)
        :return:
        """
        print("Please see below for the available bots")
        example_count: int = 0
        for startpath in startpaths:
            for root, _, files in os.walk(startpath):

                level = root.replace(startpath, "").count(os.sep)
                indent = " " * 4 * level
                if os.path.basename(root) == "__pycache__":
                    continue

                print(f"{indent}{os.path.basename(root)}/")
                subindent = " " * 4 * (level + 1)

                for file_name in files:
                    # Only want to present YAML files to the user
                    if os.path.splitext(file_name)[1] != ".yaml":
                        continue

                    # Do not present an entry in the filter list
                    if file_name in self.YAML_FILTER_LIST:
                        continue

                    # Assign the path to a number
                    self.num_path_map[example_count] = os.path.abspath(
                        os.path.join(root, file_name)
                    )

                    print(f"{str(example_count).rjust(3, ' ')}.{subindent}{file_name}")

                    example_count += 1

    def prompt_user(self) -> None:
        """
        Ask the user for a valid path number.
        :return:
        """
        rtn_val: str = input("Please enter the number of the bot to run...\n")
        while True:
            try:
                rtn_num = int(rtn_val)
            except ValueError:
                rtn_val = input("Not a valid bot number. Please enter again...\n")
                continue

            if rtn_num not in self.num_path_map:
                rtn_val = input("Number did not correspond to a bot - please try again\n")
                continue

            self.target_bot = self.num_path_map[rtn_num]
            break

    def run_bot(self) -> None:
        """
        With the path to the bot in hand, run it.
        :return:
        """
        print(f"Running bot at {self.target_bot}")

        load_and_run_bot(self.target_bot)


def no_args_main() -> None:
    """
    If no arguments are passed to the function, assumes that we want the listing view of all
    available examples.
    Including ones from installed plugins.
    :return:
    """
    NoArgsMainRunner()


def one_arg_main() -> None:
    """
    Run an example from a single path.
    :param target_path:
    :return:
    """
    load_and_run_bot(sys.argv[1])


def load_and_run_bot(yaml_path: str) -> None:
    """
    Load and run a bot from a given path.
    :param yaml_path:
    :return:
    """
    assert os.path.isfile(
        yaml_path
    ), f"Error - cannot run bot at {yaml_path} - yaml file does not exist"

    with open(yaml_path, "r", encoding="utf-8") as config:
        bot = mewbot.loader.configure_bot("DemoBot", config)

    bot.run()


if __name__ == "__main__":

    if len(sys.argv) == 1:
        no_args_main()
        sys.exit(0)

    if len(sys.argv) != 2:
        print("Usage", sys.argv[0], " [configuration name]")
        sys.exit(1)

    one_arg_main()
