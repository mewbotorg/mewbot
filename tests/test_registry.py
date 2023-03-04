# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

import abc
from typing import Any, Type

import pytest

from mewbot.core import ComponentKind
from mewbot.api.registry import ComponentRegistry
from mewbot.api.v1 import Condition, InputEvent


class TestRegistry:
    @staticmethod
    def test_class_registration() -> None:
        """Test the standard registration process by making a Condition"""

        class Condiment(Condition, abc.ABC):
            pass

        assert Condiment in ComponentRegistry.registered

    # noinspection PyUnusedLocal
    @staticmethod
    def test_class_double_registration() -> None:
        """Test error registering a class which implements two API versions"""

        error = "Class tests.test_registry.Pepper inherits from two APIs"

        @ComponentRegistry.register_api_version(ComponentKind.Condition, "double")
        class Condiment(Condition, abc.ABC):
            pass

        with pytest.raises(TypeError, match=error):

            class Pepper(Condiment, Condition, abc.ABC):  # pylint:disable=unused-variable
                pass

    @staticmethod
    def test_api_registration() -> None:
        """Test registering a class as a new API version"""

        @ComponentRegistry.register_api_version(ComponentKind.Condition, "test")
        class Condiment(abc.ABC, metaclass=ComponentRegistry):
            @staticmethod
            @abc.abstractmethod
            def consumes_inputs() -> set[Type[InputEvent]]:
                pass

            @abc.abstractmethod
            def allows(self, event: InputEvent) -> bool:
                pass

        api_versions = ComponentRegistry._api_versions  # pylint: disable="protected-access"
        condition_apis = api_versions.get(ComponentKind.Condition, {})
        assert condition_apis.get("test") == Condiment

    @staticmethod
    def test_api_registration_outside_meta() -> None:
        error = "^Can not register an API version from a non-registered class$"

        class Condiment:  # pylint: disable=too-few-public-methods
            pass

        register = ComponentRegistry.register_api_version(ComponentKind.Condition, "test-1")
        with pytest.raises(TypeError, match=error):
            register(Condiment)  # type: ignore

    @staticmethod
    def test_api_registration_without_kind() -> None:
        error = r"^Component kind 'None' not valid \(must be one of \[.*\]\)$"

        class Condiment(
            metaclass=ComponentRegistry
        ):  # pylint: disable=too-few-public-methods
            pass

        with pytest.raises(TypeError, match=error):
            ComponentRegistry.register_api_version(None, "test")(Condiment)  # type: ignore

    @staticmethod
    def test_api_registration_without_version() -> None:
        error = "^Can not register an API class '.*' without an API version$"
        with pytest.raises(ValueError, match=error):
            ComponentRegistry.register_api_version(ComponentKind.Condition, "")(Condition)

    @staticmethod
    def test_api_registration_without_protocol() -> None:
        error = "^<class '.*'> does not meet the contract of a Condition$"

        class Condiment(
            metaclass=ComponentRegistry
        ):  # pylint: disable=too-few-public-methods
            pass

        register = ComponentRegistry.register_api_version(ComponentKind.Condition, "test-3")
        with pytest.raises(TypeError, match=error):
            register(Condiment)  # type: ignore

    @staticmethod
    def test_api_re_registration() -> None:
        error = "^Can not register <class '.*'> as API version v1 for Condition; already registered"
        with pytest.raises(ValueError, match=error):
            ComponentRegistry.register_api_version(ComponentKind.Condition, "v1")(Condition)

    @staticmethod
    def test_class_api_detection() -> None:
        class Foo(Condition):
            @staticmethod
            def consumes_inputs() -> set[Type[InputEvent]]:
                return set()

            def allows(self, event: InputEvent) -> bool:
                return True

        assert ComponentRegistry.api_version(Foo) == (ComponentKind.Condition, "v1")
        assert ComponentRegistry.api_version(Foo()) == (ComponentKind.Condition, "v1")

    @staticmethod
    def test_non_registry_class_api_detection() -> None:
        with pytest.raises(ValueError):
            ComponentRegistry.api_version(str)  # type: ignore

    @staticmethod
    def test_class_creation_unregistered() -> None:
        with pytest.raises(TypeError, match="Attempting to create a non registered class"):
            ComponentRegistry.__call__(str)  # type: ignore

    @staticmethod
    def test_class_creation() -> None:
        """Tests creating a Registry managed class with various property schemes.

        Position arguments are passed through directly to the __init__ function,
        along with any keyword arguments that do not map to a settable property
        on the class. This includes passing through values for read-only properties
        or non-property attributes (such as methods).

        Writeable properties are written to before the init time."""

        class Pepper(Condition):
            _args: tuple[Any, ...]
            _kwargs: dict[str, Any]
            _prop1: str
            _prop2: str

            def __init__(self, *args: Any, prop1: str, **kwargs: Any):
                self._args = args
                self._prop1 = prop1
                self._kwargs = kwargs

            @staticmethod
            def consumes_inputs() -> set[Type[InputEvent]]:
                return {InputEvent}

            def allows(self, event: InputEvent) -> bool:
                return True

            @property
            def prop1(self) -> str:
                return self._prop1

            @property
            def prop2(self) -> str:
                return self._prop2

            @prop2.setter
            def prop2(self, prop2: str) -> None:
                self._prop2 = prop2

            @staticmethod
            def fuzz() -> str:
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
        modules = list(ComponentRegistry.load_and_register_modules())

        assert isinstance(modules, list)
