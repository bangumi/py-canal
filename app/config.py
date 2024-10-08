import os
from urllib.parse import urlparse


broker = urlparse(os.environ.get("BROKER") or "kafka://192.168.1.3:29092")
MEMCACHED = os.environ.get("MEMCACHED", "192.168.1.3:11211")

MYSQL_HOST: str = os.getenv("MYSQL_HOST") or "127.0.0.1"
MYSQL_PORT: str = os.getenv("MYSQL_PORT") or "3306"
MYSQL_USER: str = os.getenv("MYSQL_USER") or "user"
MYSQL_PASS: str = os.getenv("MYSQL_PASS") or "password"
MYSQL_DB: str = os.getenv("MYSQL_DB") or "bangumi"
