from enum import StrEnum


class Sections(StrEnum):
    MAIN = ""
    ABOUT = "about"
    TOPICS = "hashtags"
    FEATURED = "announcements"
    CONTACTS = "about_contact_and_basic_info"


class GroupInfoKeys(StrEnum):
    NAME = "group_name"
    MEMBERS = "n_members"
    IS_PRIVATE = "is_private"
    LINK = "link"
    DESCRIPTION = "description"
    CREATION_DATE = "creation_date"
    ADMINS = "admins"
    POSTS_FREQUENCY = "daily_posts_frequency"
    WEEKLY_NEW = "weekly_new"
    LOCATIONS = "locations"
    TOPICS = "topics"
    FEATURED = "feat"


class AdminInfo(StrEnum):
    ID = "id"
    NAME = "name"
    CONTACT_INFO = "contact_info"
    SCORE = "average_score"
    N_REVIEWS = "n_reviews"


class TopicsInfo(StrEnum):
    TEXT = "tag"
    COUNT = "tagged_post_count"


class AdminContactType(StrEnum):
    MAIL = "mail"
    PHONE = "phone"
    SITE = "website"


class PostData(StrEnum):
    USER = "user_name"
    DATE = "date_posted"
    TEXT = "text"
    COMMENTS = "n_comments"
    SHARES = "n_shares"
    LIKES = "n_likes"
