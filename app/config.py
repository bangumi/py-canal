import os


broker = os.environ.get("BROKER")
memcached: str = os.environ.get("MEMCACHED")

MYSQL_HOST: str = os.getenv("MYSQL_HOST") or "127.0.0.1"
MYSQL_PORT: str = os.getenv("MYSQL_PORT") or "3306"
MYSQL_USER: str = os.getenv("MYSQL_USER") or "user"
MYSQL_PASS: str = os.getenv("MYSQL_PASS") or "password"
MYSQL_DB: str = os.getenv("MYSQL_DB") or "bangumi"
