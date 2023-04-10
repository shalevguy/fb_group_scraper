from datetime import datetime

import pytest

from enums import GroupInfoKeys
from group_filter import filter_json_2_filter_function, get_filter_func

TEST = [
    {GroupInfoKeys.IS_PRIVATE: True},
    {GroupInfoKeys.IS_PRIVATE: True, GroupInfoKeys.MEMBERS: 1000},
    {
        GroupInfoKeys.IS_PRIVATE: False,
        GroupInfoKeys.DESCRIPTION: "test text new",
        GroupInfoKeys.MEMBERS: 1000,
        GroupInfoKeys.CREATION_DATE: datetime.fromisoformat("2023-04-08"),
        GroupInfoKeys.LOCATIONS: [],
    },
    {
        GroupInfoKeys.IS_PRIVATE: False,
        GroupInfoKeys.DESCRIPTION: "test text new",
        GroupInfoKeys.MEMBERS: 100,
        GroupInfoKeys.CREATION_DATE: datetime.fromisoformat("2023-04-08"),
        GroupInfoKeys.LOCATIONS: ["test"],
    },
    {
        GroupInfoKeys.IS_PRIVATE: False,
        GroupInfoKeys.DESCRIPTION: "test text new",
        GroupInfoKeys.MEMBERS: 2000,
        GroupInfoKeys.CREATION_DATE: datetime.fromisoformat("2023-04-08"),
        GroupInfoKeys.LOCATIONS: [],
    },
    {
        GroupInfoKeys.IS_PRIVATE: False,
        GroupInfoKeys.DESCRIPTION: "test text new",
        GroupInfoKeys.MEMBERS: 1000,
        GroupInfoKeys.CREATION_DATE: datetime.fromisoformat("2023-03-08"),
        GroupInfoKeys.LOCATIONS: [],
    },
    {
        GroupInfoKeys.IS_PRIVATE: False,
        GroupInfoKeys.DESCRIPTION: "test text new",
        GroupInfoKeys.MEMBERS: 1000,
        GroupInfoKeys.CREATION_DATE: datetime.fromisoformat("2023-01-08"),
        GroupInfoKeys.LOCATIONS: [],
    },
    {
        GroupInfoKeys.IS_PRIVATE: False,
        GroupInfoKeys.DESCRIPTION: "test text old",
        GroupInfoKeys.MEMBERS: 1000,
        GroupInfoKeys.CREATION_DATE: datetime.fromisoformat("2023-01-08"),
        GroupInfoKeys.LOCATIONS: ["foo"],
    },
]


FILTER_LIST = [
    {"info_key": GroupInfoKeys.DESCRIPTION, "should_include": False, "value": "new"},
    {"info_key": GroupInfoKeys.DESCRIPTION, "should_include": False, "value": "old"},
    {"info_key": GroupInfoKeys.DESCRIPTION, "value": "old"},
    {
        "info_key": GroupInfoKeys.CREATION_DATE,
        "max_val": "2021-04-08",
    },
    {
        "info_key": GroupInfoKeys.CREATION_DATE,
        "min_val": "2023-01-28",
    },
    {
        "info_key": GroupInfoKeys.CREATION_DATE,
        "min_val": "2023-01-28",
        "max_val": "2023-02-28",
    },
    {
        "info_key": GroupInfoKeys.MEMBERS,
        "max_val": 10,
    },
    {
        "info_key": GroupInfoKeys.MEMBERS,
        "min_val": 500,
    },
    {
        "info_key": GroupInfoKeys.MEMBERS,
        "min_val": 900,
        "max_val": 1100,
    },
    {"info_key": GroupInfoKeys.LOCATIONS, "relevant_locations": ["test"]},
    {
        "info_key": GroupInfoKeys.LOCATIONS,
        "relevant_locations": ["test"],
        "strict": True,
    },
]


@pytest.mark.parametrize(
    "filter_json_indices, output_length",
    [
        ([0], 1),
        ([1], 5),
        ([2], 1),
        ([3], 0),
        ([4], 4),
        ([5], 0),
        ([6], 0),
        ([7], 5),
        ([8], 4),
        ([9], 6),
        ([10], 1),
        ([0, 5, 10], 0),
        ([1, 3, 9], 0),
    ],
)
def test_get_filter_func(filter_json_indices: list[int], output_length: int):
    filter_list = [FILTER_LIST[i] for i in filter_json_indices]
    filter_func = filter_json_2_filter_function(filter_list)
    assert len(list(filter(filter_func, TEST))) == output_length


def test_get_filter_func_when_input_is_none():
    filter_func = get_filter_func(None)
    assert len(list(filter(filter_func, TEST))) == 6
