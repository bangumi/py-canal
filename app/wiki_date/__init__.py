from dataclasses import dataclass
from collections.abc import Iterable

import msgspec
from kafka import KafkaConsumer
from loguru import logger
from sqlalchemy import text
from bgm_tv_wiki import WikiSyntaxError, parse
from kafka.consumer.fetcher import ConsumerRecord

from app import config
from app.db import create_engine
from app.model import Op, KafkaValue, SubjectType
from app.wiki_date.extract_date import extract_date


@dataclass(kw_only=True, frozen=True, slots=True)
class ChiiSubject:
    subject_id: int
    field_infobox: str
    subject_type_id: SubjectType
    subject_platform: int
    subject_ban: int


def __wiki_date_kafka_events() -> Iterable[ChiiSubject]:
    consumer = KafkaConsumer(
        "debezium.chii.bangumi.chii_subjects",
        group_id="py-cache-clean",
        bootstrap_servers=f"{config.broker.hostname}:{config.broker.port}",
        auto_offset_reset="earliest",
    )

    decoder = msgspec.json.Decoder(KafkaValue[ChiiSubject])

    msg: ConsumerRecord
    for msg in consumer:
        if not msg.value:
            continue
        value: KafkaValue[ChiiSubject] = decoder.decode(msg.value)
        before = value.payload.before
        after = value.payload.after

        if value.payload.op == Op.Delete:
            continue

        if after is None:
            continue

        if before is None:
            yield after
            continue

        if after.field_infobox != before.field_infobox:
            yield after


@logger.catch
def wiki_date() -> None:
    logger.info("start")
    engine = create_engine()

    while True:
        for subject in __wiki_date_kafka_events():
            logger.debug("event: subject wiki change {}", subject.subject_id)
            try:
                w = parse(subject.field_infobox)
            except WikiSyntaxError:
                continue

            date = extract_date(w, subject.subject_type_id, subject.subject_platform)
            if date is None:
                continue

            with engine.connect() as conn:
                conn.execute(
                    text(
                        """
                        update chii_subject_fields
                        set field_year = :year, field_mon = :month, field_date = :date
                        where field_sid = :id
                        """
                    ),
                    {
                        "year": date.year,
                        "month": date.month,
                        "date": date.to_date(),
                        "id": subject.subject_id,
                    },
                )
