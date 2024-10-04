import time
import logging
from typing import NamedTuple
from datetime import datetime, timedelta
from collections.abc import Iterable

import sslog
import msgspec
from sslog import logger
from bgm_tv_wiki import WikiSyntaxError, parse

from app.db import create_engine
from app.kafka import KafkaConsumer
from app.model import Op, SubjectType, KafkaMessageValue
from app.wiki_date.extract_date import extract_date


logging.basicConfig(handlers=[sslog.InterceptHandler()])


class ChiiSubject(msgspec.Struct):
    subject_id: int
    field_infobox: str
    subject_type_id: SubjectType
    subject_platform: int
    subject_ban: int


class ChiiSubjectRev(msgspec.Struct):
    rev_subject_id: int
    rev_field_infobox: str
    rev_type_id: SubjectType
    rev_platform: int


class SubjectChange(NamedTuple):
    subject_id: int
    infobox: str
    type_id: SubjectType
    platform: int
    ts: datetime


decoder = msgspec.json.Decoder(KafkaMessageValue[ChiiSubject])
rev_decoder = msgspec.json.Decoder(KafkaMessageValue[ChiiSubjectRev])


def __wiki_date_kafka_events() -> Iterable[SubjectChange]:
    c = KafkaConsumer(
        "debezium.chii.bangumi.chii_subjects",
        "debezium.chii.bangumi.chii_subject_revisions",
    )

    for msg in c:
        logger.debug("new kafka msg", topic=msg.topic, offset=msg.offset)

        if msg.topic.endswith("chii_subject_revisions"):
            rev: KafkaMessageValue[ChiiSubjectRev] = rev_decoder.decode(msg.value)
            if rev.after is not None:
                yield SubjectChange(
                    subject_id=rev.after.rev_subject_id,
                    infobox=rev.after.rev_field_infobox,
                    platform=rev.after.rev_platform,
                    type_id=rev.after.rev_type_id,
                    ts=rev.source.timestamp(),
                )
            continue

        value: KafkaMessageValue[ChiiSubject] = decoder.decode(msg.value)
        if value.op == Op.Delete:
            continue
        after = value.after

        if after is None:
            continue

        yield SubjectChange(
            subject_id=after.subject_id,
            infobox=after.field_infobox,
            platform=after.subject_platform,
            type_id=after.subject_type_id,
            ts=value.source.timestamp(),
        )


__no_delay_threshold = timedelta(seconds=2)


@logger.catch
def wiki_date() -> None:
    logger.info("start wiki_date")
    engine = create_engine()

    while True:
        for subject in __wiki_date_kafka_events():
            delay = datetime.now().astimezone() - subject.ts
            logger.info(
                "event: subject wiki change",
                subject_id=subject.subject_id,
                ts=subject.ts.isoformat(sep=" "),
                delay=str(delay),
            )

            # only wait if row is just edited
            if delay <= __no_delay_threshold:
                time.sleep(1)

            try:
                w = parse(subject.infobox)
            except WikiSyntaxError:
                continue

            try:
                date = extract_date(w, subject.type_id, subject.platform)
                if date is None:
                    continue

                with engine.connect() as conn:
                    with conn.begin() as txn:
                        conn.connection.cursor().execute(
                            """
                            update chii_subject_fields
                            set field_year = %s, field_mon = %s, field_date = %s
                            where field_sid = %s
                            """,
                            [
                                date.year,
                                date.month or 1,
                                date.to_date(),
                                subject.subject_id,
                            ],
                        )
                        txn.commit()
            except Exception:
                logger.exception("failed to set update subject date")


if __name__ == "__main__":
    wiki_date()
