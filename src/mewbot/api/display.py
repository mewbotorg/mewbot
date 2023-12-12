"""
Stores classes which produce a display from mewbot objects.

This display - for the moment - is mostly just text.
"""


from typing import Any

import inspect


class TextDisplay:
    """
    Provides a collection of utility functions with sensible human-readable defaults.

    These include
    - name
    - help
    - status
    - description
    """

    _internal_obj: Any

    def __init__(self, internal_object: Any) -> None:
        """
        Attach the TextDisplay class to an actual object.
        """
        self._internal_obj = internal_object

    def help(self) -> str:
        """
        Returns a human-readable help string for this InputEvent.

        Practically, should be rarely used - included for completeness.
        """
        return inspect.getsource(type(self._internal_obj))

    def name(self) -> str:
        """
        Return a human-readable display name for this InputEvent.

        Used for formatting logging statements.
        """
        return type(self._internal_obj).__name__

    def description(self) -> str:
        """
        Return a human-readable description of this InputEvent.

        Eventually, may include details such as
         - which IOConfig generated it
         - when
        """
        if (cand_str := type(self._internal_obj).__doc__) is not None:
            return cand_str
        return f"{self.name()} has no doc string set."

    def status(self) -> str:
        """
        Return a human-readable status for this InputEvent.
        """
        return f"InputEvent - {self.name()} has not had a particular status set."
