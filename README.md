# fb_group_scraper

- [fb_group_scraper](#fb-group-scraper)
  * [Overview](#overview)
    + [Main Stage - Scraping The Group About Page](#main-stage---scraping-the-group-about-page)
    + [Advanced Stage - Scraping More Pages](#advanced-stage---scraping-more-pages)
      - [Admin List Enrichment](#admin-list-enrichment)
      - [Topic List](#topic-list)
      - [Pinned Posts](#pinned-posts)
  * [Installation](#installation)
  * [Usage](#usage)
    + [CLI](#cli)
    + [Output JSON Structure](#output-json-structure)
      - [Admins Data](#admins-data)
      - [Featured Posts](#featured-posts)
    + [Group Filter](#group-filter)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


## Overview
This project is a scrapper for Facebook groups.
It as 2 main stages:
### Main Stage - Scraping The Group's About Page
In this stage the scrapper first downloads the group's about page.
In this stage the scrapper first attempts to extract the
group's description and its privacy. If the group is public
the scraper will then proceed and extract the group's creation
date, admin list, daily posts frequency, amount of weekly new posts
and the group's locations. If the group isn't public,
the rest of the information will not be extracted, as it's
unavailable.
### Advanced Stage - Scraping More Pages
This stage of the scraping process involves further crawling,
its stages are:
#### Admin List Enrichment
In this stage the scraper iterates over the retrieved
admins list and then move to each admin's page. If the admin
is a Facebook page, the scraper will try to extract its contact
information, its amount of reviews and average rating.
#### Topic List
In this stage the scrapper will crawl to the topics page
and will extract all the existing hashtags and their posts
count,
#### Pinned Posts
In this stage the scrapper will extract the group's pinned
posts

## Installation
Note: This project was developed in python 3.11 and is will not run using versions earlier than 3.10 as it uses the match case statement feature which didn't exist in earlier versions.

Steps:
1. Clone repository
2. Install poetry
3. run poetry install
4. install pre-commit
5. run playwright install

## Usage
### CLI

```
Usage: main.py [OPTIONS] DEST_DIR INPUT_PATH

Arguments:
  DEST_DIR    [required]
  INPUT_PATH  [required]

Options:
  --sleep-time INTEGER            [default: 2]
  --group-filter-loc TEXT
  --override / --no-override      [default: no-override]
  --advance-scrape / --no-advance-scrape
                                  [default: advance-scrape]
  --help                          Show this message and exit.
```

| Argument                               | Required | Default Value    | Description                                                                                                                                                                                                                                |
|----------------------------------------|----------|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| dest_dir                               | yes      | None             | String. Path of new directory to store the output files. Creates it if it doesn't exist.                                                                                                                                                   |
| input_path                             | yes      | none             | String. Path to Facebook group or to local file where each line is a different path to a facebook group.                                                                                                                                   |
| sleep_time                             | no       | 2                | Integer. The time in milliseconds that scraper should wait between making requests.                                                                                                                                                        |
| group_filter_loc                       | no       | none             | String. Local path of a file containing a json that specifies which groups should carry on to the advanced scraping stage. If not specified, the filter will be only for public groups. See the Group Filter section for more information. |
| --overwrite / --no-overwrite           | no       | --no-overwrite   | Specifies if the scraper should overwrite output files if dest_dir contains an output file for a group that the scraper is about to crawl                                                                                                  |
| --advance=scrape / --no-advance-scrape | no       | --advance-scrape | If no-advance-scrape is used, will only go through the first stage.                                                                                                                                                                        |


### Output JSON Structure
All the keys are specified in the enums.py file.

| Key                   | Type       | Description                                                                                  |
|-----------------------|------------|----------------------------------------------------------------------------------------------|
| group_name            | string     | The group's name.                                                                            |
| link                  | str        | Path to the group.                                                                           |
| is_private            | bool       | True if the group is private, False otherwise.                                               |
| n_members             | int        | Amount of group members.                                                                     |
| description           | str        | The group's description.                                                                     |
| admins                | list[dict] | List of JSONs containing information about each admin. See below.                            |
| creation_date         | str        | Group's creation date.                                                                       |
| weekly_new            | int        | Amount of weekly new posts in the group.                                                     |
| daily_posts_frequency | float      | Average daily posts frequency of the group                                                   |
| locations             | list[str]  | List of group's locations                                                                    |
| topics                | list[dict] | List of JSONs representing the group's hashtags and the amount of posts that relate to them. |
| feat                  | list[dict] | List of JSONs representing the group's pinned posts. See Below.                              |

#### Admin Data

| Key            | Type                      | Description                                                                                                    |
|----------------|---------------------------|----------------------------------------------------------------------------------------------------------------|
| id             | str                       | The admin's id.                                                                                                |
| name           | str                       | The admin's name.                                                                                              |
| contact_info   | list[dict[str,list[str]]] | List of contacts. Each key is a contact type (phone, mail, website) and the value is a list of relevant value. |
| average_score  | float                     | The admin's page's average rating                                                                              |
| n_reviews      | int                       | The amount of page reviews of the admin.                                                                       |

#### Featured Posts
| Key         | Type |
|-------------|------|
| user_name   | str  |
| date_posted | str  |
| text        | str  |
| n_comments  | int  |
| n_shares    | int  |
| n_likes     | int  |


### Group Filter
As mentioned above, when group_list_path isn't specified, the only filter that is applied is
checking if is_private is False. As there's no point in proceeding to advanced scrape, this filter is always
applied. The rest of the implemented filter should be in written in a file as a
list of dictionaries. Each dictionary should have the key info_key. The rest of
the options should be specified as described below:

| info_key_value | options                                                                                                             | description                                                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| description    | '**should_include**': bool (default: False) <br> '**value**': str                                                   | checks if the description includes (or doesn't include) value.                                                                                 |
| locations      | '**strict**': bool (default: True) <br> '**value**': list[str]                                                      | checks if the location has a none empty intersection with value. If not in strict mode, doesn't filter out groups without specified locations. |
| creation_date  | '**min_val**': date in iso formate (default: "2004-02-04") <br> '**max_val**': date in iso formate (default: today) | checks if the creation_date is between min_val and max_val.                                                                                    |
| n_members      | '**min_val**': int (default: 0) <br> '**max_val**': int (default: 3B)                                               | checks if the number of members is between min_val and max_val.                                                                                |
