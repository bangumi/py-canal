import re
from typing import NamedTuple
from datetime import date

from bgm_tv_wiki import Wiki

from app.model import SubjectType
from vendor.common.platform import PLATFORM_CONFIG


patterns = [
    re.compile(
        r"^((?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日)([^\d号発號]|$)"
    ),
    re.compile(
        r"(^[^\d-])(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\)([^\d-]|$)"
    ),
    re.compile(
        r"(^[^\d-])(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})\)([^\d/]|$)"
    ),
    re.compile(
        r"(^[^\d.])(?P<year>\d{4})\.(?P<month>\d{1,2})\.(?P<day>\d{1,2})\)([^\d.万]|$)"
    ),
    # (YYYY-MM-DD)
    re.compile(r"\((?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\)$"),
    # （YYYY-MM-DD）
    re.compile(r"（(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})）"),
    # YYYY-MM-DD
    re.compile(r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})[ ([（].*$"),
    # YYYY年(MM月)?(DD日)?
    re.compile(r"^(?P<year>\d{4})年(?:(?P<month>\d{1,2})月)?(?:(?P<day>\d{1,2})日)?"),
]


class Date(NamedTuple):
    year: int
    month: int = 0
    day: int = 0

    def to_date(self) -> date:
        return date(self.year, self.month or 1, self.day or 1)


default_sort_keys = ("放送开始", "发行日期", "开始")

platform_default_sort_keys = {
    SubjectType.Book: ("发售日", "开始"),
    SubjectType.Anime: default_sort_keys,
    SubjectType.Music: default_sort_keys,
    SubjectType.Game: default_sort_keys,
    SubjectType.Real: default_sort_keys,
}


def __get_sort_keys(subject_type: SubjectType, platform: int) -> tuple[str, ...]:
    p = PLATFORM_CONFIG.get(subject_type, {}).get(platform)
    if p is not None:
        if p.sortKeys:
            return p.sortKeys

    return platform_default_sort_keys.get(subject_type, default_sort_keys)


def extract_date(w: Wiki, subject_type: SubjectType, platform: int) -> Date | None:
    keys = __get_sort_keys(subject_type, platform)

    for key in keys:
        values = w.get_all(key)
        if not values:
            continue
        return parse_str(values[0])

    return None


def parse_str(s: str) -> Date | None:
    for pattern in patterns:
        if m := pattern.match(s):
            try:
                year = int(m.group("year"))
                if m.group("month"):
                    month = int(m.group("month"))
                else:
                    month = 0
                if m.group("day"):
                    day = int(m.group("day"))
                else:
                    day = 0
            except ValueError:
                return None
            return Date(year, month, day)

    return None
