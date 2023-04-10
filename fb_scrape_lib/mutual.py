from json import loads
from time import sleep

from playwright.sync_api import Page, sync_playwright

from enums import *

SCROLL_SIZE = 1e3
DATE = "date"
NUMBER = "number"
ADMINS_KEY = "facepile_admin_profiles"
PUBLIC = "Anyone can see who's in the group and what they post"
POSTS = "posts"
TEXT = "text"
NO_NEW_MEMBERS = "No new members in the last week"
TOPICS_STR = '"group_hashtags_with_filter":{"hashtag_query"'
LOCATIONS_KEY = "group_locations"


def __scroll_till_html_does_not_change(
    page: Page, address: str, n: int, sleep_time: int
):
    page.goto(address)
    html = ""
    i = 0
    old_length = -1
    while i < n and len(html) > old_length:
        old_length = len(html)
        page.mouse.wheel(0, SCROLL_SIZE)
        sleep(sleep_time)
        html = page.content()
    return html


def get_html(link: str, section: Sections, sleep_time: int, n_scrolls: int = 1) -> str:
    address = f"{link}{section.value}"
    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            context = browser.new_context(locale="us-EN")
            page = context.new_page()
            page.goto(address)
            html = __scroll_till_html_does_not_change(
                page, address, sleep_time, n_scrolls
            )
    return html


def get_area_around_kw(x: str, kw: str, margin: int) -> str | bool:
    """Used for inspections in debug mode"""
    if kw in x:
        ix = x.find(kw)
        start = max(0, ix - margin)
        end = min(len(x), ix + margin + 1)
        return x[start:end]


def number_string_2_int(s: str) -> int:
    return int(s.replace(",", ""))


def extract_first_json_object_in_string(text: str, curly_brackets: bool) -> dict:
    bracket_start, bracket_end = "{}" if curly_brackets else "[]"
    beginning = text.find(bracket_start)
    if beginning is None:
        return {}
    s = text[beginning:]
    count_start = 1
    count_end = 0
    pos = 1
    while count_start > count_end and pos < len(s):
        if s[pos] == bracket_start:
            count_start += 1
        elif s[pos] == bracket_end:
            count_end += 1
        pos += 1
    if count_end == count_start:
        return loads(s[:pos])
    return {}


def get_json_from_text_after(html: str, x: str, curly_brackets: bool) -> dict | None:
    ix = html.find(x)
    if ix == -1:
        return None
    s = html[ix:]
    return extract_first_json_object_in_string(s, curly_brackets)
