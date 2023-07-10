# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests the json backed data sources.
"""

import json

from mewbot.data.json_data import (
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
