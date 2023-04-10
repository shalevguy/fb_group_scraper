import pytest

from normalization import fix_link, get_group_name


@pytest.mark.parametrize(
    "text, output",
    [
        (
            "https://www.facebook.com/groups/washingtonprie/posts/889214298663124/",
            "https://www.facebook.com/groups/washingtonprie/",
        ),
        (
            "www.facebook.com/groups/WeldCountyGOP/permalink/10159805988203188/",
            "https://www.facebook.com/groups/WeldCountyGOP/",
        ),
        (
            "https://www.facebook.com/groups/category/travel-and-leisure-activities-samos-samos/4714802281875088/",
            None,
        ),
    ],
)
def test_fix_link(text: str, output: str):
    assert fix_link(text) == output


@pytest.mark.parametrize(
    "text, output",
    [
        (
            "https://www.facebook.com/groups/washingtonprie/posts/889214298663124/",
            "washingtonprie",
        ),
        (
            "www.facebook.com/groups/WeldCountyGOP/permalink/10159805988203188/",
            "WeldCountyGOP",
        ),
        (
            "https://www.facebook.com/groups/category/travel-and-leisure-activities-samos-samos/4714802281875088/",
            "category",
        ),
        ("www.google.com", None),
    ],
)
def test_get_group_name(text: str, output: str):
    assert get_group_name(text) == output
