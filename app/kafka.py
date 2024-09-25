from typing import Iterator, NamedTuple

from sslog import logger
from confluent_kafka import Consumer

from app import config


class Msg(NamedTuple):
    topic: str
    offset: int
    key: bytes | None
    value: str | bytes


class KafkaConsumer:
    def __init__(self, *topics: str):
        self.c = Consumer(
            {
                "group.id": "py-cache-clean",
                "bootstrap.servers": f"{config.broker.hostname}:{config.broker.port}",
                "auto.offset.reset": "earliest",
            }
        )
        self.c.subscribe(list(topics))

    def __iter__(self) -> Iterator[Msg]:
        while True:
            msg = self.c.poll(None)
            if msg is None:
                continue

            if msg.error():
                logger.error("consumer error", err=msg.error())
                continue

            msg_value = _ensure_binary(msg.value())
            if msg_value is None:
                continue

            yield Msg(
                topic=msg.topic() or "",
                offset=msg.offset() or 0,
                key=_ensure_binary(msg.key()),
                value=msg_value,
            )


def _ensure_binary(s: str | bytes | None) -> bytes | None:
    if isinstance(s, str):
        return s.encode()
    return s
