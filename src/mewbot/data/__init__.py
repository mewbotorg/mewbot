#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Provides core classes for DataSources and the DataStores that power them.

This allows mewbot bots to store persistent data and draw from other data sources when it comes
time to construct responses to InputEvents.
"""

from __future__ import annotations

from typing import Generic, TypeVar

import dataclasses
import datetime
import enum

DataType = TypeVar("DataType")  # pylint: disable=invalid-name


class DataModerationState(enum.IntEnum):
    """
    Holds the moderation state of a piece of data.

    In the case that data for a source must undergo moderation
     - has that moderation occurred?
     - if it has, what is the outcome?
    """

    APPROVED = 1
    PENDING = 0
    REJECTED = -1


@dataclasses.dataclass
class DataRecord(Generic[DataType]):
    """
    Represents an individual entry in a :class DataSource: - an individual piece of data.
    """

    value: DataType
    created: datetime.datetime
    status: DataModerationState
    source: str


class DataStoreEmptyException(Exception):
    """
    Raised when a DataStore doesn't have a value to return.
    """
