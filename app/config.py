import os

import yarl
from dotenv import load_dotenv

load_dotenv()

broker = yarl.URL(os.environ["BROKER"])
memcached: str = os.environ["MEMCACHED"]
COMMIT_REF: str = os.environ.get("COMMIT_REF", "dev")

if __name__ == "__main__":
    print(f"{broker=}")
    print(f"{memcached=}")
    print(f"{COMMIT_REF=}")
