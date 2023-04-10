import re
from datetime import datetime, timedelta
from typing import Any, Callable

from bs4 import BeautifulSoup
from dateparser import parse

from normalization import FB_PREFIX

from .mutual import *

RATING_REGEX = re.compile(
    r"Rating · (?P<rating>\d(\.\d+)?) \((?P<n_reviews>(\d+|\d{1,3}(,\d{3})*)) Reviews\)"
)
NOT_YET_RATED_REGEX = re.compile(
    r"Not yet rated \((?P<n_reviews>(\d+|\d{1,3}(,\d{3})*)) Reviews\)"
)
SPAN = "span"
POST_CLASS = "x9f619 x1n2onr6 x1ja2u2z x2bj2ny x1qpq9i9 xdney7k xu5ydu1 xt3gfkd xh8yej3 x6ikm8r x10wlt62 xquyuld"
LIKES_CLASS = "x16hj40l"
CONTACT_INFO_CLASS = "x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h"
CLASS = "class"
NONE_TEXT_CONTENT = "xi81zsa"
SHARED_A_LINK = " shared a link"
DIV = "div"

DATE_IX = 1
USER_NAME_IX = 0

POST_CLASS_DICT = {CLASS: POST_CLASS}
LIKES_CLASS_DICT = {CLASS: LIKES_CLASS}
CONTACT_INFO_CLASS_DICT = {CLASS: CONTACT_INFO_CLASS}
POST_CLASSES = [
    "x193iq5w",
    "xeuugli",
    "x13faqbe",
    "x1vvkbs",
    "xlh3980",
    "xvmahel",
    "x1n0sxbx",
]


def get_topic_data(item: dict) -> dict[str, object]:
    d = item["node"]
    return {TopicsInfo.TEXT: d[TopicsInfo.TEXT], TopicsInfo.COUNT: d[TopicsInfo.COUNT]}


def get_topics(link: str, sleep_time: int) -> list[dict[str, object]]:
    html = get_html(link, Sections.TOPICS, sleep_time)
    j = get_json_from_text_after(html, TOPICS_STR, True)
    if j:
        topics = j["hashtag_query"]["edges"]
        return [get_topic_data(item) for item in topics]
    return []


def parse_post_date(text: str):
    if "·" not in text:
        return None
    text = text.split("·")[1]
    if "d" in text:
        delta = int(text.replace("d", ""))
        today = datetime.now()
        d = timedelta(days=delta)
        return (today - d).strftime("%d/%m/%Y")
    return parse(text).strftime("%d/%m/%Y")


def post_2_text(element):
    spans = element.find_all(SPAN)
    for cls in POST_CLASSES:
        spans = [span for span in spans if cls in span.attrs.get(CLASS, [])]
    texts = [x.get_text() for x in spans]
    content = [
        text
        for i, text in enumerate(texts)
        if NONE_TEXT_CONTENT not in spans[i].attrs["class"]
    ]
    return [x for x in texts if x], content


def get_comments_and_shares_indices_from_element_texts(
    texts,
) -> (int | None, int | None):
    for i, x in enumerate(texts[:-1]):
        comments_section = x.split()[-1] == "Comments"
        split_text = texts[i + 1].split()
        if comments_section and split_text[-1] == "Shares":
            return i, i + 1
        if comments_section and split_text[0] == "View":
            return i, None
    return None, None


def extract_post_data(element) -> dict[str, object]:
    texts, assumed_text = post_2_text(element)
    if len(texts) == 0:
        return {}
    date_ix = DATE_IX
    name = texts[USER_NAME_IX]
    if SHARED_A_LINK in name:
        date_ix = DATE_IX + 1
        name = name.split(SHARED_A_LINK)[0]
    name = " ".join(name.split())
    date = parse_post_date(texts[date_ix])
    if date is None:
        return {}
    comments_ix, shares_jx = get_comments_and_shares_indices_from_element_texts(texts)
    if comments_ix:
        content = "".join(texts[date_ix + 1 : comments_ix])
        comments_str = texts[comments_ix].split()[0]
        n_comments = number_string_2_int(comments_str)
        if shares_jx:
            shares_str = texts[comments_ix + 1].split()[0]
            n_shares = number_string_2_int(shares_str)
        else:
            n_shares = 0

    else:
        content = " ".join(assumed_text)
        n_comments = 0
        n_shares = 0
    likes_span = element.find(SPAN, LIKES_CLASS)
    if likes_span:
        n_likes = number_string_2_int(likes_span.get_text())
    else:
        n_likes = 0
    return {
        PostData.USER: name,
        PostData.DATE: date,
        PostData.TEXT: content,
        PostData.COMMENTS: n_comments,
        PostData.SHARES: n_shares,
        PostData.LIKES: n_likes,
    }


def get_featured(link: str, sleep_time: int) -> list[dict[str, object]]:
    html = get_html(link, Sections.FEATURED, sleep_time, n_scrolls=50)
    soup = BeautifulSoup(html, features="html.parser")
    elements = soup.find_all(DIV, POST_CLASS)
    res = []
    for i, elm in enumerate(elements):
        try:
            post_data = extract_post_data(elm)
            if post_data:
                res.append(post_data)
        except:
            pass
    return res


def is_mail(x: str) -> bool:
    return "@" in x and len(x.split()) == 1


def is_website(x: str) -> bool:
    return "http" in x and len(x.split()) == 1


def is_phone(x: str) -> bool:
    clean_input = re.sub(r"\W+", "", x)
    clean_input = re.sub(r"\s", "", clean_input)
    try:
        int(clean_input)  # only digits
        return True
    except ValueError:
        return False


def map_filter_type_to_filter_func(
    contact_type: AdminContactType,
) -> Callable[[str], bool]:
    match contact_type:
        case AdminContactType.MAIL:
            return is_mail
        case AdminContactType.SITE:
            return is_website
        case AdminContactType.PHONE:
            return is_phone


def filter_contact_type_from_spans(
    contact_type: AdminContactType, span_texts: list[str]
) -> list[str]:
    filter_func = map_filter_type_to_filter_func(contact_type)
    return list(filter(filter_func, span_texts))


def get_admin_contact_info(span_texts: list[str]) -> dict[AdminContactType, str]:
    return {
        ct: filter_contact_type_from_spans(ct, span_texts) for ct in AdminContactType
    }


def get_rating(span_texts: list[str]) -> dict[AdminInfo, Any] | None:
    for text in span_texts:
        if m := RATING_REGEX.match(text):
            return {
                AdminInfo.SCORE: float(m.group("rating")),
                AdminInfo.N_REVIEWS: number_string_2_int(m.group("n_reviews")),
            }
        if m := NOT_YET_RATED_REGEX.match(text):
            return {
                AdminInfo.SCORE: 0.0,
                AdminInfo.N_REVIEWS: int(m.group("n_reviews")),
            }
    return {AdminInfo.SCORE: 0.0, AdminInfo.N_REVIEWS: 0}


def enrich_admin(link: str, sleep_time: int) -> dict[AdminInfo, Any]:
    html = get_html(link, Sections.ABOUT, sleep_time)
    res = {}
    if html.find("Contact info") > 0:
        soup = BeautifulSoup(html, features="html.parser")
        contact_spans = soup.find_all(SPAN, CONTACT_INFO_CLASS_DICT)
        span_texts = [" ".join(x.get_text().split()) for x in contact_spans]
        res[AdminInfo.CONTACT_INFO] = get_admin_contact_info(span_texts)
        res |= get_rating(span_texts)
    return res


def enrich(admins_lst: list[dict[str, Any]], sleep_time: int):
    links = [FB_PREFIX + x[AdminInfo.ID] + "/" for x in admins_lst]
    enriched_data = [enrich_admin(link, sleep_time) for link in links]
    return [x | enriched_data[i] for i, x in enumerate(admins_lst)]


def get_advanced_json(
    link: str, sleep_time: int, admins_list: list[dict[str, Any]]
) -> dict:
    topics = get_topics(link, sleep_time)
    feat = get_featured(link, sleep_time)
    enriched_admins_list = enrich(admins_list, sleep_time)
    return {
        GroupInfoKeys.TOPICS: topics,
        GroupInfoKeys.FEATURED: feat,
        GroupInfoKeys.ADMINS: enriched_admins_list,
    }
