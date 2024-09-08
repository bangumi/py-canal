import os
from urllib.parse import urlparse


broker = urlparse(os.environ.get("BROKER") or "kafka://192.168.1.3:29092")
memcached = urlparse(os.environ.get("MEMCACHED") or "192.168.1.3:11211")

MYSQL_HOST: str = os.getenv("MYSQL_HOST") or "127.0.0.1"
MYSQL_PORT: str = os.getenv("MYSQL_PORT") or "3306"
MYSQL_USER: str = os.getenv("MYSQL_USER") or "user"
MYSQL_PASS: str = os.getenv("MYSQL_PASS") or "password"
MYSQL_DB: str = os.getenv("MYSQL_DB") or "bangumi"

redis_dsn = os.environ.get("REDIS_DNS") or "redis://:redis-pass@192.168.1.3:6379/0"
