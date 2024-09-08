from threading import Thread

from app.wiki_date import wiki_date


def main():
    threads = [
        Thread(target=wiki_date),
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
