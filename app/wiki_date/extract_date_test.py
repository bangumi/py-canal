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
    assert parse_str("2024.5.18（预售）") == Date(2024, 5, 18)
    assert parse_str("2024-05-01（预售）") == Date(2024, 5, 1)
    assert parse_str("2024.10.12（预售）") == Date(2024, 10, 12)
    assert parse_str("2024.10.12") == Date(2024, 10, 12)


@pytest.mark.parametrize(
    ["infobox", "type_id", "platform", "date"],
    [
        (
            ["{{Infobox animanga/Novel", "|发售日= 1886-01-05", "}}"],
            SubjectType.Book,
            0,
            Date(1886, 1, 5),
        ),
        (
            ["{{Infobox animanga/Novel", "|放送开始={", "[1999-02-28]", "}", "}}"],
            SubjectType.Anime,
            0,
            Date(1999, 2, 28),
        ),
        [
            """
{{Infobox animanga/Novel"
|发售日={
[2024-09-28（旭儒预售）]
[2023-08-12（星文预售）]
}
}}
        """.splitlines(),
            SubjectType.Book,
            0,
            Date(2024, 9, 28),
        ],
        [
            """
{{Infobox animanga/TVAnime
|中文名= Bangumi Wiki 动画测试用沙盘
|别名={
[Wiki Sandbox]
[沙盒少女 test]
}
|话数= 9
|放送开始={
[1998-11-01]
[1996-01-01 (test)]
}
}}""".splitlines(),
            SubjectType.Anime,
            5,
            Date(1998, 11, 1),
        ],
        [
            """
{{Infobox Game
|发行日期= 2025
}}
""".splitlines(),
            SubjectType.Game,
            4041,
            Date(2025, 0, 0),
        ],
        [
            """
{{Infobox Game
|发行日期= 2025-01
}}
""".splitlines(),
            SubjectType.Game,
            4041,
            Date(2025, 1),
        ],
        [
            """
{{Infobox Game
|发行日期= 2025-5
}}
""".splitlines(),
            SubjectType.Game,
            4041,
            Date(2025, 5),
        ],
        [
            """
{{Infobox Game
|发行日期= 2025年4月
}}
""".splitlines(),
            SubjectType.Game,
            4041,
            Date(2025, 4),
        ],
    ],
)
def test_extract_date(
    infobox: list[str],
    type_id: SubjectType,
    platform: int,
    date: Date,
) -> None:
    actual = extract_date(parse("\n".join(infobox)), type_id, platform)
    assert actual == date
