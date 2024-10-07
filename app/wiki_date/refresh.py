import itertools

from tqdm import tqdm
from sqlalchemy import text
from bgm_tv_wiki import WikiSyntaxError, parse

from app.db import create_engine
from app.wiki_date.extract_date import extract_date


def main() -> None:
    engine = create_engine()
    with (
        engine.begin() as conn,
        conn.execution_options(yield_per=100).execute(
            text(
                """
            SELECT subject_id,subject_type_id,subject_platform,field_infobox,field_year,field_mon
            FROM chii_subjects
            INNER JOIN chii_subject_fields ON field_sid = subject_id
            where (
                subject_ban = 0
                AND field_redirect = 0
            )
            order by subject_id;
            """
            ),
        ) as result,
    ):
        for (
            subject_id,
            subject_type_id,
            subject_platform,
            field_infobox,
            field_year,
            field_mon,
        ) in tqdm(itertools.chain.from_iterable(result.partitions()), ascii=True):
            try:
                w = parse(field_infobox)
            except WikiSyntaxError:
                continue

            date = extract_date(w, subject_type_id, subject_platform)
            if date.year == field_year and field_mon == date.month:
                continue

            with engine.begin() as txn:
                txn.execute(
                    text(
                        """
                        update chii_subject_fields
                        set field_year = :year, field_mon = :month, field_date = :date
                        where field_sid = :subject_id
                        """
                    ),
                    {
                        "year": date.year,
                        "month": date.month,
                        "date": date.to_date(),
                        "subject_id": subject_id,
                    },
                )


if __name__ == "__main__":
    main()
