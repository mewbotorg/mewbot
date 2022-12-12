from typing import Dict, Any, Set, Type

from mewbot.api.registry import ComponentRegistry
from mewbot.api.v1 import Action, Trigger, InputEvent, OutputEvent
from mewbot.manager import BasicManager


class TestRegistry:
    @staticmethod
    def test_cannot_multiple_inherit() -> None:
        """
        Tests that we cannot create a class multiply inheriting from several
        base classes.
        :return:
        """
        try:

            class TerribleExampleClass(Action, Trigger):
                async def run(self) -> None:
                    raise RuntimeError("Whatever you're doing? Probably a bad plan.")

                @staticmethod
                def consumes_inputs() -> Set[Type[InputEvent]]:
                    """
                    InputClasses the trigger has registered an interest in.
                    :return:
                    """
                    return set()

                @staticmethod
                def produces_outputs() -> Set[Type[OutputEvent]]:
                    """
                    Output event classes which can be produced by this action.
                    :return:
                    """
                    return set()

                async def act(self, event: InputEvent, state: Dict[str, Any]) -> None:
                    """
                    Ultimately responsible for transforming InputEvents into OutputEvents.
                    :param event:
                    :param state:
                    :return:
                    """
                    raise NotImplementedError("This position should not be reached")

                def matches(self, event: InputEvent) -> bool:
                    """
                    Returns True or False if the event is of interest to the Action.
                    :param event:
                    :return:
                    """
                    return bool(event)

            test_class = TerribleExampleClass()
            assert test_class is None, "Something has gone _very_ wrong"
        except TypeError:
            pass

    @staticmethod
    def test_registry_api_version() -> None:
        """
        Try to use the ComponentRegistry to register a component twice.
        :return:
        """
        ComponentRegistry.api_version(BasicManager())
