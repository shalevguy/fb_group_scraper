from datetime import datetime
from functools import partial
from json import loads
from pathlib import Path
from typing import Callable

from fb_scrape_lib.mutual import GroupInfoKeys

MAX = "max_val"
MIN = "min_val"
FB_LAUNCH_DATE = "2004-02-04"


def check_if_public(json: dict) -> bool:
    return not json[GroupInfoKeys.IS_PRIVATE]


def check_all(value: dict, func_list: list[Callable[[dict], bool]]) -> bool:
    for func in func_list:
        if not func(value):
            return False
    return True


def only_from_locations(
    json: dict, relevant_locations: list[str], strict: bool
) -> bool:
    if locations := json[GroupInfoKeys.LOCATIONS]:
        for location in locations:
            if location in relevant_locations:
                return True
    return not strict


def key_within_range(json: dict, key: GroupInfoKeys, value_range: (object, object)):
    return value_range[0] < json[key] < value_range[1]


def check_substring_existence(json, substring, should_include):
    if should_include:
        return substring in json[GroupInfoKeys.DESCRIPTION]
    return substring not in json[GroupInfoKeys.DESCRIPTION]


def match_item_func(item):
    match item["info_key"]:
        case GroupInfoKeys.LOCATIONS.value:
            relevant_locations = item.get("relevant_locations", None)
            strict = item.get("strict", False)
            return partial(
                only_from_locations,
                relevant_locations=relevant_locations,
                strict=strict,
            )
        case GroupInfoKeys.MEMBERS.value:
            max_val = item.get(MAX, 3e9)
            min_val = item.get(MIN, 0)
            return partial(
                key_within_range,
                value_range=[min_val, max_val],
                key=GroupInfoKeys.MEMBERS,
            )
        case GroupInfoKeys.CREATION_DATE.value:
            if max_val := item.get(MAX):
                max_val = datetime.fromisoformat(max_val)
            else:
                max_val = datetime.today()
            if min_val := item.get(MIN):
                min_val = datetime.fromisoformat(min_val)
            else:
                min_val = datetime.fromisoformat(FB_LAUNCH_DATE)
            return partial(
                key_within_range,
                value_range=[min_val, max_val],
                key=GroupInfoKeys.CREATION_DATE,
            )
        case GroupInfoKeys.DESCRIPTION:
            substring = item.get("value")
            if substring is None:
                raise ValueError("a description filter without value is not allowed")
            should_include = item.get("should_include", True)
            return partial(
                check_substring_existence,
                substring=substring,
                should_include=should_include,
            )
        case _:
            raise NotImplemented(f"filter not implemented for {item['info_key']}")


def filter_json_2_filter_function(filter_json: list[dict]) -> Callable[[dict], bool]:
    func_list = [check_if_public] + [match_item_func(item) for item in filter_json]
    return partial(check_all, func_list=func_list)


def get_filter_func(group_filter_loc: str | None) -> Callable[[dict], bool]:
    if group_filter_loc is None:
        return check_if_public
    path = Path(group_filter_loc)
    if not path.exists():
        raise RuntimeError("could not find filter json")
    with open(group_filter_loc, "r") as f:
        filter_json = loads(f.read())
    return filter_json_2_filter_function(filter_json)
