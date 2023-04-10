import datetime
import re
from typing import Any

from bs4 import BeautifulSoup
from dateparser import parse

from enums import *

from .mutual import *

# regexes

MEMBERS_REGEX = re.compile(r"dir=\"auto\">\s*(?P<number>\S+) total members")
CREATION_DATE_REGEX = re.compile(r"Group created on (?P<date>.*? 20\d\d)")
POSTS_LAST_MONTH_REGEX = re.compile(
    r"(?P<posts>\d{1,3}(,\d{3})*(\.\d+)?)\s*<!-- -->\s* in the last month"
)
NEW_MEMBERS_THIS_WEEK_REGEX = re.compile(
    r"\"group_new_members_info_text\":\"(?P<text>.*?)\""
)


LINK = "a"
CONTENT = "content"

MONTH = 30

DESCRIPTION_COMPONENT_OPTIONS = [
    ["meta", {"name": "description"}],
    ["meta", {"property": "og:image:alt"}],
]


def __get_members(html: str) -> int:
    amount = MEMBERS_REGEX.search(html)
    if amount:
        return number_string_2_int(amount.group(NUMBER))
    return 0


def __get_full_description(soup: BeautifulSoup) -> str | None:
    options = []
    for option in DESCRIPTION_COMPONENT_OPTIONS:
        if x := soup.find(*option):
            options.append(x.get(CONTENT, ""))
            options.append(x.attrs.get(CONTENT, ""))
        else:
            options.append("")
    return max(options, key=len)


def __get_date(html: str) -> datetime.datetime:
    date = CREATION_DATE_REGEX.search(html).group(DATE)
    return parse(date)


def get_details(admin_dict: dict):
    node = admin_dict["node"]
    return {AdminInfo.ID: node[AdminInfo.ID], AdminInfo.NAME: node[AdminInfo.NAME]}


def __get_admins(html) -> list[dict[str, str]]:
    j = get_json_from_text_after(html, ADMINS_KEY, True)
    if j:
        admin_details = [get_details(x) for x in j["edges"]]
        admin_details.sort(key=lambda x: x[AdminInfo.ID])
        return admin_details
    return []


def __is_public(html) -> bool:
    return PUBLIC in html


def __get_monthly_posts_frequency(html: str) -> float:
    amount_match = POSTS_LAST_MONTH_REGEX.search(html)
    if amount_match is None:
        return 0.0
    amount = number_string_2_int(amount_match.group(POSTS))
    return amount / MONTH


def __get_weekly_new_members(html: str) -> float:
    amount_match = NEW_MEMBERS_THIS_WEEK_REGEX.search(html)
    if amount_match is None:
        return 0.0
    amount_string = amount_match.group(TEXT)
    if NO_NEW_MEMBERS == amount_string:
        return 0.0
    return float(amount_string)


def __get_more_info_from_about_for_public_group(
    html: str,
) -> dict[GroupInfoKeys, Any]:
    return {
        GroupInfoKeys.MEMBERS: __get_members(html),
        GroupInfoKeys.CREATION_DATE: __get_date(html),
        GroupInfoKeys.ADMINS: __get_admins(html),
        GroupInfoKeys.POSTS_FREQUENCY: __get_monthly_posts_frequency(html),
        GroupInfoKeys.WEEKLY_NEW: __get_weekly_new_members(html),
        GroupInfoKeys.LOCATIONS: __get_locations(html),
    }


def __get_locations(html: str) -> list[str]:
    j = get_json_from_text_after(html, LOCATIONS_KEY, False)
    if j:
        locations = [item["name"] for item in j]
        locations.sort()
        return locations
    return []


def get_info_from_about(link: str, sleep_time: int) -> dict[GroupInfoKeys, Any]:
    html = get_html(link, Sections.ABOUT, sleep_time)
    soup = BeautifulSoup(html, features="html.parser")
    description = __get_full_description(soup)
    result = {GroupInfoKeys.DESCRIPTION: description}
    if not __is_public(html):
        result[GroupInfoKeys.IS_PRIVATE] = True
        return result
    result[GroupInfoKeys.IS_PRIVATE] = False
    more_information_about_group = __get_more_info_from_about_for_public_group(html)
    return result | more_information_about_group
