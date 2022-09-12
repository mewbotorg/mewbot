#!/usr/bin/env python3
# pylint: disable=duplicate-code
# this is an example - duplication for emphasis is desirable
# A minimum viable discord bot - which just responds with a set message to every input

from __future__ import annotations

from typing import Any, Dict, Set, Type, List, Tuple, Optional

import dataclasses
import logging
import random
import re

from mewbot.api.v1 import Trigger, Action
from mewbot.core import InputEvent, OutputEvent, OutputQueue
from mewbot.io.discord import DiscordMessageCreationEvent, DiscordOutputEvent


class DiscordDiceMaidenCommandTrigger(Trigger):
    """
    Nothing fancy - just fires whenever there is a DiscordTextInputEvent
    """

    _command: str = ""

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        return {DiscordMessageCreationEvent}

    @property
    def command_prefix(self) -> str:
        return self._command

    @command_prefix.setter
    def command_prefix(self, command: str) -> None:
        self._command = str(command)

    def matches(self, event: InputEvent) -> bool:
        if not isinstance(event, DiscordMessageCreationEvent):
            return False

        return event.text == self._command


class DiscordDiceMaidenResponseAction(Action):
    """
    Print every InputEvent.
    """

    _logger: logging.Logger
    _queue: OutputQueue
    _message: str = ""

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__ + type(self).__name__)

    @staticmethod
    def consumes_inputs() -> Set[Type[InputEvent]]:
        return {DiscordMessageCreationEvent}

    @staticmethod
    def produces_outputs() -> Set[Type[OutputEvent]]:
        return {DiscordOutputEvent}

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        self._message = str(message)

    async def act(self, event: InputEvent, state: Dict[str, Any]) -> None:
        """
        Construct a DiscordOutputEvent with the result of performing the calculation.
        """
        if not isinstance(event, DiscordMessageCreationEvent):
            self._logger.warning("Received wrong event type %s", type(event))
            return

        test_event = DiscordOutputEvent(
            text=self._message, message=event.message, use_message_channel=True
        )

        await self.send(test_event)


@dataclasses.dataclass
class RollResult:

    input_token: str
    output_array: List[int]
    result: str
    child_results: Optional[List[RollResult]] = None


class DiceRoller:
    """
    Preforms the work of actually parsing a dice string into something meaningful,
    rolling it and then returning it.
    """
    # Symbolic operations
    math_tokens = (r"+", r"-", r"//", r"*")

    # Triggers on "d12", "4d4 + 3d6" e.t.c
    simple_dice_re = r"([0-9]+)?[dD][0-9]+"
    dice_add_re = r"([0-9]+)?[dD][0-9]+[\-\+\*\\](([0-9]+)?[dD][0-9]+)?[0-9]+?"

    def __call__(self, roll_str: str) -> str:
        tokens = self.tokenize(roll_str)

        rolled_tokens = []
        for token in tokens:
            rolled_tokens.append(self.process_token(token))

        return self.render_tokens(rolled_tokens)

    def render_tokens(self, roll_results: List[RollResult]) -> str:
        """
        Take a list of tokens and render it using the guidelines.
        """
        rtn_str = ""
        for token in roll_results:
           rtn_str += str(token.result)
        return rtn_str

    def process_token(self, token: str) -> RollResult:
        """
        Process a token in the form of a string.
        """
        try:
            int(token)
            return RollResult(input_token=token, output_array=[], result=token)
        except ValueError:
            pass

        if re.fullmatch(self.simple_dice_re, token):
            return self.process_simple_dice_token(token)

        if re.fullmatch(self.dice_add_re, token):
            return self.process_compound_dice_token(token)

        raise NotImplementedError(f"Token - {token} - could not be processed")

    @staticmethod
    def process_simple_dice_token(simple_dice_token) -> RollResult:
        """
        Process a simple dice token - a string in the form "ndm"
        """
        count, dice = simple_dice_token.split("d")
        count, dice = int(count), int(dice)

        array = [random.randint(1, dice) for _ in range(count)]

        return RollResult(input_token=simple_dice_token, output_array=array, result=str(sum(array)))

    def process_compound_dice_token(self, compound_dice_token) -> RollResult:
        """
        Process a compound dice token - a string in the form "ndm+pdq" or "ndm+p"
        """
        final_tokens: List[str] = []

        acc_str: str = ""
        for char in compound_dice_token:
            if char in self.math_tokens:
                final_tokens.append(acc_str)
                final_tokens.append(char)
                acc_str = ""
                continue
            acc_str += char
        if acc_str:
            final_tokens.append(acc_str)

        # Sum and produce the answer
        result: int = 0
        mode: str = "+"
        output_list: List[RollResult] = []
        for token in final_tokens:
            if token in self.math_tokens:
                mode = token
                continue

            output_list.append(self.process_token(token))
            value = int(output_list[-1].result)
            if mode == "+":
                result += value
                continue
            elif mode == "-":
                result -= value
                continue

        return RollResult(input_token="".join(final_tokens), output_array=[], result=str(result), child_results=output_list)

    @staticmethod
    def tokenize(roll_str: str) -> List[str]:
        """
        Tokenize a roll string - grouping elements as required for later parsing.
        """
        if not roll_str:
            return []

        roll_str = re.sub(r"\+", " + ", roll_str)
        rs_tokens = re.split(r"\s+", roll_str)

        new_tokens = []
        for token_pos in range(len(rs_tokens)):

            token = rs_tokens[token_pos].lower()
            if not token:
                continue

            if token in ("+", "-") and (token_pos == 0 or token_pos == len(rs_tokens)):
                raise NotImplementedError("+ sign at the start or end of the str")

            # In this case we have tokens before and after
            if token in ("+", "-"):
                new_tokens[-1] += token + rs_tokens[token_pos + 1]
                # Blank so it'll be ignored on the next step
                rs_tokens[token_pos + 1] = ""
                continue

            new_tokens.append(token)

        assert True is False, new_tokens

        return new_tokens









# - subcommands
# - a combined trigger and response would be really good
# - likewise being able to specify all of this in yaml
# - preferences - which you can edit
# - tests defined right into the yaml
# - checking for the datastores so no one stores b64 encoded porn


# Tests

test_dice_roller = DiceRoller()
# assert test_dice_roller.tokenize("3d6") == ["3d6", ]
# assert test_dice_roller.tokenize(" 3d6") == ["3d6", ]
# assert test_dice_roller.tokenize(" 3d6+5") == ["3d6+5", ]
# assert test_dice_roller.tokenize(" 3d6 +   5") == ["3d6+5", ]
# assert int(test_dice_roller("3d6")) in range(3, 18)
# assert int(test_dice_roller("3d6+5")) in range(8, 23)
assert True is False, test_dice_roller("3d6+4d8")
