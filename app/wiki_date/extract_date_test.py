import pytest

from app.model import SubjectType
from app.wiki_date.extract_date import Date, parse_str


def test_parse_date():
    assert parse_str("") is None
    assert parse_str("2020年1月3日") == Date(2020, 1, 3)
    assert parse_str("2017-12-22(2018年1月5日・12日合併号)") == Date(2017, 12, 22)
    assert parse_str("2025年") == Date(2025)


@pytest.mark.parametrize(
    ["infobox", "type_id", "platform"],
    [
        (
            ["{{Infobox animanga/Novel", "|发售日= 1886-01-05", "}}"],
            SubjectType.Book,
            Date(1886, 1, 5),
        ),
    ],
)
def test_extract_date(infobox, type_id, platform):
    pass
