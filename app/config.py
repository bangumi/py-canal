import os

import yarl
from dotenv import load_dotenv as _load_dotenv


_load_dotenv()

broker = yarl.URL(os.environ["BROKER"])
memcached: str = os.environ["MEMCACHED"]
COMMIT_REF: str = os.environ.get("COMMIT_REF", "dev")

MYSQL_HOST: str = os.getenv("MYSQL_HOST") or "127.0.0.1"  # type: ignore
MYSQL_PORT: int = os.getenv("MYSQL_PORT") or 3306  # type: ignore
MYSQL_USER: str = os.getenv("MYSQL_USER") or "user"  # type: ignore
MYSQL_PASS: str = os.getenv("MYSQL_PASS") or "password"  # type: ignore
MYSQL_DB: str = os.getenv("MYSQL_DB") or "bangumi"  # type: ignore


if __name__ == "__main__":
    print(f"{broker=}")
    print(f"{memcached=}")
    print(f"{COMMIT_REF=}")
