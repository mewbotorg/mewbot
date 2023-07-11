#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tooling for recording the creation of implementation classes, allowing for lists.

Automation for registering components and plugins with a MewBot runner.

Plugins are loaded using the metadata from python packages.
Any package that exposes a `mewbot-v1` entrypoint will be assumed to contain
components that can be used.

This module also contains the ABCMeta subclass 'Registry'. All classes that use
this as their metaclass will be recorded, forming an index of all loaded components.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

import abc
import uuid

import importlib_metadata

from mewbot.core import Component, ComponentKind

# This is the magic string needed when defining the entry points to have components
# declared in a plugin automatically registered at registry startup
API_DISTRIBUTIONS = ["mewbot-v1"]


# noinspection PyMethodParameters
class ComponentRegistry(abc.ABCMeta):
    """
    Metaclass for Registering Component Classes.

    ComponentRegistry is a AbstractBaseClasses MetaClass which instruments
    class definition to automatically record and classify classes implementing
    MewBot's interfaces, and then modifies instance creation to assign properties.

    A base class, or API version, is registered using the
    ComponentRegistry.register_api_version decorator, which maps an Interface
    and API version to that base class. Any class which extends that base class
    will be registered, and can then be seen in the registered class list for
    that interface.

    The registry also enforces certain constraints; a class can not extends more
    than one base class (i.e. can not implement multiple API version nor can it
    implement multiple APIs).

    When an instance of one of the registered class is created, it is assigned
    a UUID, and any parameters which match properties are initialised.
    Any remaining properties are then passed to the underlying constructor.
    """

    registered: list[type[Any]] = []
    uuid: str  # This property is unused but fixes some linting issues in __call__

    _api_versions: dict[ComponentKind, dict[str, type[Component]]] = {}

    def __new__(mcs, name: str, bases: Any, namespace: Any, **k: Any) -> type[Any]:
        """
        Hook for creating a class in this ancestry.

        We confirm that is only implements one API, and then register it for later use
        """

        created_type: type[Any] = super().__new__(mcs, name, bases, namespace, **k)

        api_bases = list(mcs._detect_api_versions(created_type))
        if len(api_bases) > 1:
            raise TypeError(
                f"Class {created_type.__module__}.{created_type.__name__} inherits from two APIs"
            )

        ComponentRegistry.registered.append(created_type)
        return created_type

    def __call__(  # type: ignore
        cls: type[Component], *args: Any, uid: str | None = None, **properties: Any
    ) -> Any:
        """
        Meta-constructor for components.

        When an instance of one of the registered class is created, it is assigned
        a UUID, and any parameters which match properties are initialised.
        Any remaining properties are then passed to the underlying constructor.
        """

        if cls not in ComponentRegistry.registered:
            raise TypeError("Attempting to create a non registered class")

        obj: Any = cls.__new__(cls)  # pylint: disable=no-value-for-parameter
        obj.uuid = uid if uid else uuid.uuid4().hex

        _dir = dir(cls)
        to_delete = []

        for prop, value in properties.items():
            if prop not in _dir:
                continue

            if not isinstance(getattr(cls, prop), property):
                continue

            if getattr(cls, prop).fset:
                setattr(obj, prop, value)
                to_delete.append(prop)

        for prop in to_delete:
            properties.pop(prop)

        # If the remaining args and properties do not match the __init__ function
        # of the class, this call will TypeError.
        # For classes created with mewbot.loader, this indicates the wrong number of properties
        # are specified in the yaml block.
        obj.__init__(*args, **properties)

        return obj

    @classmethod
    def register_api_version(
        mcs, kind: ComponentKind, version: str
    ) -> Callable[[type[Component]], type[Component]]:
        """
        Decorator that registers an (abstract) class as an API implementation.

        The decorated class must be in the registry (generally by using the registry
        as the metaclass), implement the protocol for the give ComponentKind, and
        have a unique API version.
        """

        def do_register(api: type[Component]) -> type[Component]:
            """
            See :func:`~mewbot.ComponentRegistry.register_api_version`.

            :param api:
            :return:
            """
            if api not in mcs.registered:
                raise TypeError("Can not register an API version from a non-registered class")

            if not isinstance(kind, ComponentKind):
                raise TypeError(
                    f"Component kind '{kind}' not valid "
                    f"(must be one of {ComponentKind.values()})"
                )

            if not version:
                raise ValueError(
                    f"Can not register an API class '{api}' without an API version"
                )

            if not issubclass(api, ComponentKind.interface(kind)):
                raise TypeError(f"{api} does not meet the contract of a {kind.value}")

            kind_apis = mcs._api_versions.setdefault(kind, {})

            if version in kind_apis:
                raise ValueError(
                    f"Can not register {api} as API version {version} for {kind.value}; "
                    f"already registered by {kind_apis[version]}"
                )

            kind_apis[version] = api

            return api

        return do_register

    @classmethod
    def _detect_api_versions(mcs, impl: type) -> Iterable[tuple[ComponentKind, str]]:
        """Finds the API version that is provided by a given implementation class."""

        for kind, apis in mcs._api_versions.items():
            for version, api in apis.items():
                if issubclass(impl, api):
                    yield kind, version

    @classmethod
    def api_version(mcs, component: Component | type[Component]) -> tuple[ComponentKind, str]:
        """
        Gets the Component Kind (e.g. 'Behaviour') and API version (e.g. 'v1') from a component.

        This function will only return the first matched type, as per the Registry's
        'one base type' constraint.
        """

        if not isinstance(component, type):
            component = type(component)

        apis = list(mcs._detect_api_versions(component))

        if len(apis) != 1:
            raise ValueError(f"No API version for {component}")

        return apis[0]

    @staticmethod
    def load_and_register_modules() -> Iterable[Any]:
        """
        Load modules from setuptools that declare an entrypoint with a supported API.

        This looks at the entrypoints of all modules which are locatable with
        importlib, and looks at their defined entry points. If a module matches
        a known entry point type, it is imported. Classes that are in the registry's
        ancestry will be automatically added to the registry for easy code discovery.

        :return: the loaded modules.
        """

        distribution: importlib_metadata.Distribution

        for distribution in importlib_metadata.distributions():
            for entry_point in distribution.entry_points:
                if entry_point.group not in API_DISTRIBUTIONS:
                    continue

                yield entry_point.load()  # pragma: no cover

    @staticmethod
    def require_package(name: str) -> Any:
        """
        Loads a named package (distribution) which presents a MewBot entrypoint.

        This function is intended to help debug plugin loading by requiring that
        the load operations succeeds, and throwing some form of exception otherwise.

        :return: the loaded module.
        """

        distribution: importlib_metadata.Distribution
        distribution = importlib_metadata.distribution(name)

        for entry_point in distribution.entry_points:
            if entry_point.group in API_DISTRIBUTIONS:
                return entry_point.load()  # pragma: no cover

        raise ModuleNotFoundError(
            f"Distribution {name} does not implement any known API ({API_DISTRIBUTIONS})"
        )
