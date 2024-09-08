import sqlalchemy
from sqlalchemy import Pool

from app.config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_PORT, MYSQL_USER


def create_engine() -> Pool:
    return sqlalchemy.create_engine(
        sqlalchemy.URL.create(
            drivername="mysql+pymysql",
            username=MYSQL_USER,
            password=MYSQL_PASS,
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            database=MYSQL_DB,
        ),
        pool_recycle=3600,
        isolation_level="AUTOCOMMIT",
        pool_size=10,
        max_overflow=0,
    ).pool
