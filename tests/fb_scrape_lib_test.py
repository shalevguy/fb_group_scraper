from inspect import getmodule
from json import loads
from typing import Callable
from unittest import mock

import pytest

from enums import AdminInfo
from fb_scrape_lib.advanced_scrape import (
    enrich_admin,
    get_featured,
    get_rating,
    get_topics,
    is_mail,
    is_phone,
    is_website,
)
from fb_scrape_lib.mutual import (
    GroupInfoKeys,
    extract_first_json_object_in_string,
    get_area_around_kw,
    number_string_2_int,
)
from fb_scrape_lib.scrape_about import get_info_from_about


def get_html_and_results_json_from_path(local_path: str) -> (str, dict):
    with open(f"example_groups/{local_path}.html", "r") as f:
        html = f.read()
    with open(f"example_groups/{local_path}.json", "r") as f:
        json = loads(f.read())
    return html, json


def get_mock_result_for_html(html: str, func: Callable, mocker) -> dict:
    module = getmodule(func).__name__
    with mock.patch(f"{module}.get_html", return_value=html):
        res = func("", 2)
    return res


@pytest.mark.parametrize(
    "text, output",
    [
        ("1,000", 1000),
        ("40,000", 40000),
        ("243", 243),
    ],
)
def test_number_string_2_int(text: str, output: str):
    assert number_string_2_int(text) == output


# testing on 3 biggest fb groups
@pytest.mark.parametrize(
    "link",
    [
        "https://www.facebook.com/groups/ourevergreenbangladesh/",
        "https://www.facebook.com/groups/makeupartistsgroup/",
        "https://www.facebook.com/groups/cheapmealideas/",
    ],
)
def test_get_info_from_about_manages_to_handle_links(link: str):
    res = get_info_from_about(link, 2)
    assert res[GroupInfoKeys.MEMBERS] > 0
    assert len(res[GroupInfoKeys.ADMINS]) > 0
    assert len(res[GroupInfoKeys.DESCRIPTION]) > 0


@pytest.mark.parametrize(
    "local_path, func",
    [
        ("makeupartistsgroup", get_info_from_about),
        ("cheapmealideas", get_info_from_about),
        ("cheapmealideas_featured", get_featured),
        ("makeupartistsgroup_admin", enrich_admin),
        ("cheapmealideas_topics", get_topics),
    ],
)
def test_page_scraper(local_path: str, func: Callable, mocker):
    html, json = get_html_and_results_json_from_path(local_path)
    res = get_mock_result_for_html(html, func, mocker)
    assert res == json


@pytest.mark.parametrize(
    "s, kw, margin, result",
    [
        ("1112111", "2", 1, "121"),
        ("abcdefg", "b", 3, "abcde"),
        ("test_example_three", "re", 4, "e_three"),
        ("test", "0", 2, None),
    ],
)
def test_get_area_around_kw(s: str, kw: str, margin: int, result: str):
    assert get_area_around_kw(s, kw, margin) == result


@pytest.mark.parametrize(
    "s, is_curly, result",
    [
        ("  [[]],", False, [[]]),
        ("  [[]],", True, {}),
        (
            'type:{"name": "test", "attributes": [1, 2, 3]}',
            True,
            {"name": "test", "attributes": [1, 2, 3]},
        ),
    ],
)
def test_get_area_around_kw(s: str, is_curly: bool, result: dict):
    assert extract_first_json_object_in_string(s, is_curly) == result


@pytest.mark.parametrize(
    "text, result",
    [
        ("test@test.co.uk", True),
        ("test@mail.com", True),
        ("oisheroisoo", False),
        ("test@test.co.uk sdfsd", False),
    ],
)
def test_is_mail(text: str, result: bool):
    assert is_mail(text) == result


@pytest.mark.parametrize(
    "text, result",
    [
        ("http://test.com", True),
        ("https://www.test.com", True),
        ("oisheroisoo", False),
        ("http://www.test.com sdfsd", False),
    ],
)
def test_is_website(text, result):
    assert is_website(text) == result


@pytest.mark.parametrize(
    "text, result",
    [
        ("054-122434", True),
        ("(123) 123 123)", True),
        ("+44 123123412", True),
        ("http://www.test.com sdfsd", False),
    ],
)
def test_is_phone(text, result):
    assert is_phone(text) == result


@pytest.mark.parametrize(
    "text, rating, reviews",
    [
        ("Rating · 4.7 (3,674 Reviews)", 4.7, 3674),
        ("Rating · 3 (200 Reviews)", 3, 200),
        ("Not yet rated · (0 Reviews)", 0.0, 0),
        ("http://www.test.com sdfsd", 0, 0.0),
    ],
)
def test_get_rating(text: str, rating: float, reviews: int):
    res = get_rating([text])
    assert res[AdminInfo.SCORE] == rating
    assert res[AdminInfo.N_REVIEWS] == reviews
