import enum
from typing import Generic, TypeVar

import msgspec


class Op(str, enum.Enum):
    Create = "c"
    Update = "u"
    Delete = "d"


T = TypeVar("T")


class ValuePayload(msgspec.Struct, Generic[T]):
    before: T | None
    after: T | None
    op: str  # 'r', 'c', 'd' ...


class KafkaValue(msgspec.Struct, Generic[T]):
    payload: ValuePayload[T]


class SubjectType(enum.IntEnum):
    Book = 1
    Anime = 2
    Music = 3
    Game = 4
    Real = 6
