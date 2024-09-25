import enum
from typing import Generic, TypeVar
from datetime import datetime

import msgspec


class Op(str, enum.Enum):
    Create = "c"
    Update = "u"
    Delete = "d"


T = TypeVar("T")


class Source(msgspec.Struct):
    ts_ms: int

    def timestamp(self):
        return datetime.fromtimestamp(self.ts_ms / 1000).astimezone()


class KafkaMessageValue(msgspec.Struct, Generic[T]):
    before: T | None
    after: T | None
    op: str  # 'r', 'c', 'd' ...

    source: Source


class SubjectType(enum.IntEnum):
    Book = 1
    Anime = 2
    Music = 3
    Game = 4
    Real = 6
