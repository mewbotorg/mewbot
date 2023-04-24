#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Basic example of how to load a mewbot component from yaml.
"""

from __future__ import annotations

from mewbot.io.common import ReplyAction
from mewbot.loader import load_component


def main() -> None:
    """
    Basic demo of loading a component from yaml.

    Component is a Condition.
    Information concerning the Condition loaded is printed to stdout after load.
    This also demonstrates the __str__ methods of the loaded component
    As well as it's serialized form, and the result of reloading the component from serialized data.
    (Also serves as a demo that the serialized and deserialized objects are the same)
    :return:
    """
    yaml_demo = load_component(
        {
            "kind": "Action",
            "implementation": "mewbot.io.common.ReplyAction",
            "uuid": "3f7c493b-ce05-4566-b906-54ece62804c1",
            "properties": {"message": "Hello, World!"},
        }
    )

    local_demo = ReplyAction()
    local_demo.message = "Hello, World!"

    print("Loaded from YAML-like object:  ", yaml_demo)
    print("Created and message set        ", local_demo)
    print("Serialised:                    ", local_demo.serialise())
    print("Re-loaded from serialized data:", load_component(local_demo.serialise()))


if __name__ == "__main__":
    main()
