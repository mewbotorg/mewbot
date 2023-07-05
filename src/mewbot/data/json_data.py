# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
This is a collection of DataSources and DataStores which use Json as a backend.

A file on disk is (somewhat) ill suited to being the backend for a data storage system which might
be accessed from multiple threads - using an intermediary which can provide such properties as
 - atomicity
 - thread safety
 - access controls
is a good idea.
Thus, even for the json backed datastores, they may use an intermediary such as a database before
the data is ultimately written out to disc.
"""

from typing import Any, Callable, Iterable, Optional, TypeVar

import json
import os
import random

from mewbot.api.v1 import DataSource
from mewbot.data import DataStoreEmptyException

DataType = TypeVar("DataType")  # pylint: disable=invalid-name


class JsonStringDataSourceSingleValue(DataSource[DataType]):
    """
    Load some data from a json string and present it - in immutable form - to the user.
    """

    # The store value of the datatype for retrieval
    stored_val: DataType
    # A map to turn any value into an instance of the datatype
    data_type_mapper: Callable[
        [
            Any,
        ],
        DataType,
    ]

    def __init__(
        self,
        json_string: str,
        data_type_mapper: Callable[
            [
                Any,
            ],
            DataType,
        ],
    ) -> None:
        """
        Startup a JsonStringDataSource - reding the value in from the given string.

        :param json_string:
        :param data_type_mapper:
        """
        loaded_value = json.loads(json_string)
        self.stored_val = data_type_mapper(loaded_value)

        self.data_type_mapper = data_type_mapper

    def get(self) -> DataType:
        """
        In this case, just returns the value of the stored datatype.
        """
        return self.stored_val

    def random(self) -> DataType:
        """
        Does slightly different things depending on the actual datatype.
        """
        return self.stored_val


class JsonFileDataSourceSingleValue(DataSource[DataType]):
    """
    Load some data out of a json file and present it - in read only format - to the user.

    Reloading data from disk is not supported.
    """

    json_file_path: Optional[os.PathLike[str]]
    stored_val: DataType
    # A map to turn any value into an instance of the datatype
    data_type_mapper: Callable[
        [
            Any,
        ],
        DataType,
    ]

    def __init__(
        self,
        json_file_path: os.PathLike[str],
        data_type_mapper: Callable[
            [
                Any,
            ],
            DataType,
        ],
    ) -> None:
        """
        Startup a JsonFileDataSource - reading the stored value in from the given file.

        :param json_file_path:
        """
        self.json_file_path = json_file_path

        self.data_type_mapper = data_type_mapper

        with open(self.json_file_path, "r", encoding="utf-8") as json_file_in:
            self.stored_val = self.data_type_mapper(json.load(json_file_in))

    def get(self) -> DataType:
        """
        There's only one value in this store - return it.

        :return:
        """
        return self.stored_val

    def random(self) -> DataType:
        """
        There's only one variable store in this class - return it.

        :return:
        """
        return self.stored_val


class JsonStringDataSourceIterableValues(DataSource[DataType]):
    """
    Load some data from a json string in the form of a list of values.

    Each of the values from the json string must conform to a valid type - same as the type
    declared.
    """

    # The store value of the datatype for retrieval
    stored_val: Iterable[DataType]

    # A map to turn any value into an instance of the datatype
    data_type_mapper: Callable[
        [
            Any,
        ],
        DataType,
    ]

    def get(self) -> DataType:
        """
        Returns the first element from the datasource.

        In this case, the first value from the iterator.
        :return:
        """
        if not self.stored_val:
            raise DataStoreEmptyException(
                f"{self.stored_val = } did not contain a value to return"
            )

        return self.stored_val.__next__()

    def __len__(self) -> int:
        """
        Return the number of values stored from the json list.

        This method exhaust the iterator before returning.
        If there is a more efficient way for the interator you want, subclass it and use it.
        :return:
        """
        return len(list(self.stored_val))

    def random(self) -> DataType:
        """
        Return a random value from the list.

        This method exhaust the iterator before returning.
        If there is a more efficient way for the interator you want, subclass it and use it.
        :return:
        """
        return random.choice([_ for _ in self.stored_val])


class JsonStringDataSourceListValues(JsonStringDataSourceIterableValues[DataType]):
    """
    Load some data from a json string in the form of a list of values.

    Each of the values from the json string must conform to a valid type - same as the type
    declared.
    """

    # The store value of the datatype for retrieval
    stored_val: list[DataType]
    # A map to turn any value into an instance of the datatype
    data_type_mapper: Callable[
        [
            Any,
        ],
        DataType,
    ]

    def __init__(
        self,
        json_string: str,
        data_type_mapper: Callable[
            [
                Any,
            ],
            DataType,
        ],
    ) -> None:
        """
        Startup a JsonStringDataSource - reding the value in from the given string.

        :param json_string:
        :param data_type_mapper:
        """
        loaded_value = json.loads(json_string)
        self.stored_val = [data_type_mapper(_) for _ in loaded_value]

        self.data_type_mapper = data_type_mapper

        clean_vals: list[DataType] = []
        for val in loaded_value:
            try:
                clean_vals.append(self.data_type_mapper(val))
            except Exception as exp:
                raise NotImplementedError(
                    f"{val = } is not a valid instance of {data_type_mapper = }"
                ) from exp

    def __len__(self) -> int:
        """
        Return the number of values stored from the json list.

        :return:
        """
        return len(self.stored_val)

    def random(self) -> DataType:
        """
        Return a random value from the list.

        :return:
        """
        return random.choice(self.stored_val)
