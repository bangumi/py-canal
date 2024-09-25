from collections.abc import Iterable

import msgspec
import pymemcache
from sslog import logger

from app import config
from app.kafka import KafkaConsumer
from app.model import KafkaMessageValue


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
    consumer = KafkaConsumer("debezium.chii.bangumi.chii_subject_interests")

    decoder = msgspec.json.Decoder(KafkaMessageValue[ChiiInterest])
    for msg in consumer:
        value: KafkaMessageValue[ChiiInterest] = decoder.decode(msg.value)
        before = value.before
        after = value.after
        if after is not None:
            yield after.interest_uid, after.interest_subject_id
        elif before is not None:
            yield before.interest_uid, before.interest_subject_id


@logger.catch
def clean_cache() -> None:
    if not config.MEMCACHED:
        return
    logger.info("start clean_cache")
    client = pymemcache.Client(config.MEMCACHED)
    v = client.version().decode()
    logger.info("memcached version {}", v)
    while True:
        for user_id, subject_id in clean_cache_kafka_events():
            logger.debug("event: user {} subject {}", user_id, subject_id)
            client.delete(f"prg_ep_status_{user_id}", True)  # MC_PRG_STATUS
            client.delete(f"prg_watching_v3_{user_id}", True)  # MC_PRG_WATCHING


if __name__ == "__main__":
    clean_cache()
