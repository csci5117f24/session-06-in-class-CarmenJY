
""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""

from contextlib import contextmanager
import logging
import os

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None


def setup():
    global pool
    DATABASE_URL = os.environ["DATABASE_URL"]
    # current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode="require")


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
        cursor = connection.cursor(cursor_factory=DictCursor)
        # cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()


def get_colors():
    with get_db_cursor(False) as cur:
        cur.execute("select * from color;")
        return cur.fetchall()


def get_color(color_code):
    with get_db_cursor(False) as cur:
        cur.execute("select * from color where color = %s;", (color_code,))
        return cur.fetchone()


def create_color(color_code, name):
    with get_db_cursor(True) as cur:
        cur.execute(
            "insert into color(color, name) values (%s, %s);", (color_code, name)
        )


if __name__ == "__main__":
    setup()
    print(get_color("#ffff00"))
