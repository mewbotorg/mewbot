# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests the json backed data sources.
"""
import json
import os.path
import tempfile

from mewbot.data import DataStoreEmptyException
from mewbot.data.json_data import (
    JsonFileDataSourceSingleValue,
    JsonStringDataSourceListValues,
    JsonStringDataSourceSingleValue,
)


class TestJsonDataTypes:
    """
    Tests the Json backed data types.
    """

    def test_json_data_source_declared_str(self) -> None:
        """
        Tests a json data source, which has been declared to have type int.
        """
        test_string_json_source = JsonStringDataSourceSingleValue[str]

        test_string_json_source(json.dumps("This is a test string"), str)

    def test_json_data_source_list_values_json_int_str(self) -> None:
        """
        Tests a json data source, loaded from a list of integers.

        :return:
        """
        test_int_list = [1, 2, 3, 453, -23, 17]

        test_json_int_list = json.dumps(test_int_list)

        test_list_source = JsonStringDataSourceListValues[int](test_json_int_list, int)

        assert isinstance(test_list_source.random(), int)
        assert len(test_list_source) == 6

        assert test_list_source.get() == 1

    def test_json_data_source_list_values_throws_type_error_mixed_list(self) -> None:
        """
        Tests a json data source fails to initialize, when loaded with an inconsistent list.

        :return:
        """
        test_mixed_list = [1, 2, 3, "this is where things break", 4, 5]

        test_json_mixed_list = json.dumps(test_mixed_list)

        try:
            JsonStringDataSourceListValues[int](test_json_mixed_list, int)
        except ValueError:
            pass

    def test_json_data_source_single_value(self) -> None:
        """
        Tests a Json data source with a single value.

        :return:
        """
        test_json_val = 55
        test_json_str = json.dumps(test_json_val)

        test_single_val_json = JsonStringDataSourceSingleValue[int](test_json_str, int)

        assert test_single_val_json.get() == test_json_val
        assert test_single_val_json.random() == test_json_val

        try:
            test_single_val_json["this should cause a NotImplementedError"]
        except NotImplementedError:
            pass

        try:
            test_single_val_json.keys()
        except NotImplementedError:
            pass

    def test_json_data_source_json_file_single_value(self) -> None:
        """
        Load a single valued json source from a file.

        :return:
        """
        test_json_val = 55

        with tempfile.TemporaryDirectory() as temp_dir:
            json_test_file = os.path.join(temp_dir, "test_json_file.json")
            with open(json_test_file, "w", encoding="utf-8") as test_json_file:
                json.dump(test_json_val, test_json_file)

            test_single_val_json = JsonFileDataSourceSingleValue[int](json_test_file, int)

            assert test_single_val_json.get() == test_json_val
            assert test_single_val_json.random() == test_json_val

            try:
                test_single_val_json["this should cause a NotImplementedError"]
            except NotImplementedError:
                pass

            try:
                test_single_val_json.keys()
            except NotImplementedError:
                pass

    def test_json_data_source_list_values_json_empty_datastore(self) -> None:
        """
        Tests a json data source, loaded from a list of integers.

        :return:
        """
        test_int_list: list[int] = []

        test_json_int_list = json.dumps(test_int_list)

        test_list_source = JsonStringDataSourceListValues[int](test_json_int_list, int)

        try:
            assert test_list_source.get() == 1
        except DataStoreEmptyException:
            pass

        assert len(test_list_source) == 0
