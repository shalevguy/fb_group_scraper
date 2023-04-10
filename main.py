from datetime import date, datetime
from json import dumps, load
from logging import getLogger
from os import mkdir
from pathlib import Path
from time import sleep

import typer
from tqdm import tqdm

from fb_scrape_lib import *
from group_filter import get_filter_func
from normalization import *

LOGGER = getLogger("main_logger")
SLEEP_TIME_MS = 2


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.strftime("%d/%m/%Y")
    raise TypeError("Type %s not serializable" % type(obj))


def load_json(path: Path):
    with open(path, "r") as f:
        return load(f)


def save_json(path: Path, json: dict):
    with open(path, "w") as f:
        s = dumps(json, indent=4, default=json_serial)
        f.write(s)
    return json


def item_to_basic_info_json(link: str, local_path: Path, sleep_time: int) -> dict:
    json = get_info_from_about(link, sleep_time)
    json[GroupInfoKeys.NAME] = get_group_name(link)
    json[GroupInfoKeys.LINK] = link
    save_json(local_path, json)
    return json


def item_to_advance_info_json(local_path: Path, json: dict, sleep_tine: int):
    json |= get_advanced_json(
        json[GroupInfoKeys.LINK], sleep_tine, json[GroupInfoKeys.ADMINS]
    )
    save_json(local_path, json)


def get_inputs_list(input_path: str) -> list[str]:
    if Path(input_path).exists:
        with open(input_path, "r") as f:
            return f.read().split()
    LOGGER.warning("path was not found locally, treating it like a webpage path")
    return [input_path]


def get_proper_input_list(lst: list[str], results_path: Path) -> list[dict]:
    links_lst = [fix_link(x) for x in lst]
    return [
        {"link": x, "local_path": results_path / (get_group_name(x) + ".json")}
        for x in links_lst
        if x
    ]


def handle_override_for_list(items: list[dict], override: bool) -> list[dict]:
    existing_files = [x for x in items if x["local_path"].exists()]
    n_existing = len(existing_files)
    if n_existing > 0:
        if override:
            LOGGER.info(f"overriding {n_existing} files")
        else:
            items = [x for x in items if not x["local_path"].exists()]
            LOGGER.info(f"ignoring {n_existing} items")
    return items


def main(
    dest_dir: str,
    input_path: str,
    sleep_time: Optional[int] = typer.Option(SLEEP_TIME_MS),
    group_filter_loc: Optional[str] = typer.Option(None),
    override: bool = False,
    advance_scrape: bool = True,
):
    group_filter_func = get_filter_func(group_filter_loc)
    results_path = Path(dest_dir)
    if not results_path.exists():
        LOGGER.info(f"the directory {dest_dir} doesn't exists. creating it")
        mkdir(results_path)
    lst = get_inputs_list(input_path)
    if len(lst) > 0:
        items = get_proper_input_list(lst, results_path)
        LOGGER.debug(f"found {len(items)} good links")
        items = handle_override_for_list(items, override)
        for item in tqdm(items):
            json = item_to_basic_info_json(**item, sleep_time=sleep_time)
            if advance_scrape and group_filter_func(json):
                sleep(sleep_time)
                item_to_advance_info_json(item["local_path"], json, sleep_time)
    else:
        LOGGER.info("no input found")


if __name__ == "__main__":
    typer.run(main)
