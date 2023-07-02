from collections.abc import Iterable

import msgspec
import pymemcache
from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from loguru import logger

from app import config


class ChiiInterest(msgspec.Struct):
    interest_id: int
    interest_uid: int
    interest_subject_id: int
    interest_subject_type: int
    interest_rate: int
    interest_type: int
    interest_has_comment: int
    interest_comment: str
    interest_tag: str
    interest_ep_status: int
    interest_vol_status: int
    interest_wish_dateline: int
    interest_doing_dateline: int
    interest_collect_dateline: int
    interest_on_hold_dateline: int
    interest_dropped_dateline: int
    interest_create_ip: str
    interest_lasttouch_ip: str
    interest_lasttouch: int
    interest_private: int


class ValuePayload(msgspec.Struct):
    before: ChiiInterest | None
    after: ChiiInterest | None
    op: str  # 'r', 'c', 'd' ...


class Value(msgspec.Struct):
    payload: ValuePayload


def kafka_events() -> Iterable[tuple[int, int]]:
    consumer = KafkaConsumer(
        "debezium.chii.bangumi.chii_subject_interests",
        group_id="py-cache-clean",
        bootstrap_servers=f"{config.broker.host}:{config.broker.port}",
        auto_offset_reset="earliest",
    )

    msg: ConsumerRecord
    for msg in consumer:
        value = msgspec.json.decode(msg.value, type=Value)
        before = value.payload.before
        after = value.payload.after
        if after is not None:
            yield after.interest_uid, after.interest_subject_id
        elif before is not None:
            yield before.interest_uid, before.interest_subject_id


@logger.catch
def main():
    logger.info("start")
    client = pymemcache.Client(config.memcached)
    while True:
        for user_id, subject_id in kafka_events():
            logger.debug("event: user {} subject {}", user_id, subject_id)
            client.delete(f"{user_id}:{subject_id}", True)


if __name__ == "__main__":
    main()
