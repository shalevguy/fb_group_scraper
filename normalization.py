import re
from typing import Optional

FB_PREFIX = "https://www.facebook.com/"
FB_GROUP_PREFIX = f"{FB_PREFIX}groups/"
FB_GROUP_REGEX = re.compile(r"(https?://)?(www)?facebook.com/groups/(?P<name>[^/)]*)/?")
CATEGORY = "category"


def get_group_name(link: str) -> Optional[str]:
    match = FB_GROUP_REGEX.search(link)
    if match:
        return match.group("name")


def fix_link(link: str) -> Optional[str]:
    name = get_group_name(link)
    if name and name != CATEGORY:
        return FB_GROUP_PREFIX + name + "/"
