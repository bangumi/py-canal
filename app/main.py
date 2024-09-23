from threading import Thread

from sslog import logger

from app import config
from app.wiki_date import wiki_date
from app.clean_cache import clean_cache


def main() -> None:
    logger.info("app start", broker=config.broker)
    threads = [
        Thread(target=clean_cache),
        Thread(target=wiki_date),
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
