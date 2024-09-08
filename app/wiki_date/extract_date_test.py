import pytest
from bgm_tv_wiki import parse

from app.model import SubjectType
from app.wiki_date.extract_date import Date, parse_str, extract_date


def test_parse_date() -> None:
    assert parse_str("") is None
    assert parse_str("2020年1月3日") == Date(2020, 1, 3)
    assert parse_str("2017-12-22(2018年1月5日・12日合併号)") == Date(2017, 12, 22)
    assert parse_str("2025年") == Date(2025)
    assert parse_str("1886-01-05") == Date(1886, 1, 5)


@pytest.mark.parametrize(
    ["infobox", "type_id", "platform", "date"],
    [
        (
            ["{{Infobox animanga/Novel", "|发售日= 1886-01-05", "}}"],
            SubjectType.Book,
            0,
            Date(1886, 1, 5),
        ),
    ],
)
def test_extract_date(
    infobox: list[str],
    type_id: SubjectType,
    platform: int,
    date: Date,
) -> None:
    assert extract_date(parse("\n".join(infobox)), type_id, platform) == date
