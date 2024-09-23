from collections.abc import Iterable

import msgspec
import pymemcache
from kafka import KafkaConsumer
from loguru import logger
from kafka.consumer.fetcher import ConsumerRecord

from app import config
from app.model import KafkaValue


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


def clean_cache_kafka_events() -> Iterable[tuple[int, int]]:
    consumer = KafkaConsumer(
        "debezium.chii.bangumi.chii_subject_interests",
        group_id="py-cache-clean",
        bootstrap_servers=f"{config.broker.hostname}:{config.broker.port}",
        auto_offset_reset="earliest",
    )

    msg: ConsumerRecord
    decoder = msgspec.json.Decoder(KafkaValue[ChiiInterest])
    for msg in consumer:
        if not msg.value:
            continue
        value = decoder.decode(msg.value)
        before = value.payload.before
        after = value.payload.after
        if after is not None:
            yield after.interest_uid, after.interest_subject_id
        elif before is not None:
            yield before.interest_uid, before.interest_subject_id


@logger.catch
def clean_cache() -> None:
    logger.info("start")
    client = pymemcache.Client(
        server=(config.memcached.hostname, config.memcached.port)
    )
    v = client.version().decode()
    logger.info("memcached version {}", v)
    while True:
        for user_id, subject_id in clean_cache_kafka_events():
            logger.debug("event: user {} subject {}", user_id, subject_id)
            client.delete(f"prg_ep_status_{user_id}", True)  # MC_PRG_STATUS
            client.delete(f"prg_watching_v3_{user_id}", True)  # MC_PRG_WATCHING
