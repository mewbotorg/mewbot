# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Preforms tests on the registry.

A system-wide, abc based class registration system.
"""

from __future__ import annotations

from typing import Any, Type

import abc

import pytest

from mewbot.api.display import TextDisplay
from mewbot.api.registry import ComponentRegistry
from mewbot.api.v1 import Condition, InputEvent
from mewbot.core import ComponentKind


class TestRegistry:
    """
    Preform registry tests.
    """

    @staticmethod
    def test_class_registration() -> None:
        """Test the standard registration process by making a Condition."""

        class Condiment(Condition, abc.ABC):
            """
            Private class for testing.
            """

        assert Condiment in ComponentRegistry.registered

    # noinspection PyUnusedLocal
    @staticmethod
    def test_class_double_registration() -> None:
        """Test error registering a class which implements two API versions."""

        error = "Class test_registry.Pepper inherits from two APIs"

        @ComponentRegistry.register_api_version(ComponentKind.Condition, "double")
        class Condiment(Condition, abc.ABC):
            """
            Private class for testing.
            """

        with pytest.raises(TypeError, match=error):

            class Pepper(Condiment, Condition, abc.ABC):  # pylint:disable=unused-variable
                """
                Private class for testing.
                """

    @staticmethod
    def test_api_registration() -> None:
        """Test registering a class as a new API version."""

        @ComponentRegistry.register_api_version(ComponentKind.Condition, "test")
        class Condiment(abc.ABC, metaclass=ComponentRegistry):
            """
            Private class for testing.
            """

            @property
            @abc.abstractmethod
            def display(self) -> TextDisplay:
                """
                May provide a display for this object - might not.
                """

            @staticmethod
            @abc.abstractmethod
            def consumes_inputs() -> set[Type[InputEvent]]:
                """
                Will not produce helpful results.
                """

            @abc.abstractmethod
            def allows(self, event: InputEvent) -> bool:
                """
                Does not, actually, allow anything.
                """

        api_versions = ComponentRegistry._api_versions  # pylint: disable="protected-access"
        condition_apis = api_versions.get(ComponentKind.Condition, {})
        assert condition_apis.get("test") == Condiment

    @staticmethod
    def test_api_registration_outside_meta() -> None:
        """
        Tests registration of a class outside mewbot class hierarchies fails.
        """
        error = "^Can not register an API version from a non-registered class$"

        class Condiment:  # pylint: disable=too-few-public-methods
            """
            Private class for testing.
            """

        register = ComponentRegistry.register_api_version(ComponentKind.Condition, "test-1")
        with pytest.raises(TypeError, match=error):
            register(Condiment)  # type: ignore

    @staticmethod
    def test_api_registration_without_kind() -> None:
        """
        Tests attempted registration of an invalid type fails.
        """
        error = r"^Component kind 'None' not valid \(must be one of \[.*\]\)$"

        class Condiment(
            metaclass=ComponentRegistry
        ):  # pylint: disable=too-few-public-methods
            """
            Private class for testing.
            """

        with pytest.raises(TypeError, match=error):
            ComponentRegistry.register_api_version(None, "test")(Condiment)  # type: ignore

    @staticmethod
    def test_api_registration_without_version() -> None:
        """
        Tests registration with a null API version fails.
        """
        error = "^Can not register an API class '.*' without an API version$"
        with pytest.raises(ValueError, match=error):
            ComponentRegistry.register_api_version(ComponentKind.Condition, "")(Condition)

    @staticmethod
    def test_api_registration_without_protocol() -> None:
        """
        Tests registration of a class without a valid interface fails.
        """
        error = "^<class '.*'> does not meet the contract of a Condition$"

        class Condiment(
            metaclass=ComponentRegistry
        ):  # pylint: disable=too-few-public-methods
            """
            Private class for testing.
            """

        register = ComponentRegistry.register_api_version(ComponentKind.Condition, "test-3")
        with pytest.raises(TypeError, match=error):
            register(Condiment)  # type: ignore

    @staticmethod
    def test_api_re_registration() -> None:
        """
        Tests that you cannot register a valid class with a valid api twice.
        """
        error = "^Can not register <class '.*'> as API version v1 for Condition; already registered"
        with pytest.raises(ValueError, match=error):
            ComponentRegistry.register_api_version(ComponentKind.Condition, "v1")(Condition)

    @staticmethod
    def test_class_api_detection() -> None:
        """
        Tests that the registry can detect the API version of a given class.
        """

        class Foo(Condition):
            """
            Private class for testing.
            """

            @staticmethod
            def consumes_inputs() -> set[Type[InputEvent]]:
                """
                Returns the empty set.
                """
                return set()

            def allows(self, event: InputEvent) -> bool:
                """
                Allows everything.
                """
                return True

        assert ComponentRegistry.api_version(Foo) == (ComponentKind.Condition, "v1")
        assert ComponentRegistry.api_version(Foo()) == (ComponentKind.Condition, "v1")

    @staticmethod
    def test_non_registry_class_api_detection() -> None:
        """
        Tests attempting to ascertain the API version of a non registered class fails.
        """
        with pytest.raises(ValueError):
            ComponentRegistry.api_version(str)  # type: ignore

    @staticmethod
    def test_class_creation_unregistered() -> None:
        """
        Tests that Attempting to create a non registered class fails.
        """
        with pytest.raises(TypeError, match="Attempting to create a non registered class"):
            ComponentRegistry.__call__(str)  # type: ignore

    @staticmethod
    def test_class_creation() -> None:
        """
        Tests creating a Registry managed class with various property schemes.

        Position arguments are passed through directly to the __init__ function,
        along with any keyword arguments that do not map to a settable property
        on the class. This includes passing through values for read-only properties
        or non-property attributes (such as methods).

        Writeable properties are written to before the init time.
        """

        class Pepper(Condition):
            """
            Private class for testing.
            """

            _args: tuple[Any, ...]
            _kwargs: dict[str, Any]
            _prop1: str
            _prop2: str

            def __init__(self, *args: Any, prop1: str, **kwargs: Any):
                """
                Init for private class for testing.
                """
                self._args = args
                self._prop1 = prop1
                self._kwargs = kwargs

            @staticmethod
            def consumes_inputs() -> set[Type[InputEvent]]:
                """
                Consumes any InputEvent.
                """
                return {InputEvent}

            def allows(self, event: InputEvent) -> bool:
                """
                Allows everything.
                """
                return True

            @property
            def prop1(self) -> str:
                """
                Testing prop1.
                """
                return self._prop1

            @property
            def prop2(self) -> str:
                """
                Testing prop2.
                """
                return self._prop2

            @prop2.setter
            def prop2(self, prop2: str) -> None:
                self._prop2 = prop2

            @staticmethod
            def fuzz() -> str:
                """
                Private function for testing.
                """
                return "fuzzy!"

        instance = Pepper("a", 1, prop1="foo", prop2="bar", prop3="baz", fuzz="fuzz")

        assert instance._args == ("a", 1)  # pylint: disable="protected-access"
        assert instance._kwargs == {  # pylint: disable="protected-access"
            "prop3": "baz",
            "fuzz": "fuzz",
        }
        assert instance._prop1 == "foo"  # pylint: disable="protected-access"
        assert instance._prop2 == "bar"  # pylint: disable="protected-access"
        assert instance.prop1 == "foo"
        assert instance.prop2 == "bar"

    @staticmethod
    def test_load_and_register_modules() -> None:
        """
        Tests that the ComponentRegistry load_and_register_modules runs and produces a list.
        """
        modules = list(ComponentRegistry.load_and_register_modules())

        assert isinstance(modules, list)

    @staticmethod
    def test_require_package_not_installed() -> None:
        """
        Tests attempting to require a package which is not installed fails.
        """
        with pytest.raises(
            ModuleNotFoundError, match="No package metadata was found for fdfdsfsd"
        ):
            ComponentRegistry.require_package("fdfdsfsd")

    @staticmethod
    def test_require_package_no_entrypoint() -> None:
        """
        Tests a package unrelated to mewbot does not present a mewbot entry point.
        """
        with pytest.raises(
            ModuleNotFoundError,
            match="Distribution pytest does not implement any known API .*",
        ):
            ComponentRegistry.require_package("pytest")
