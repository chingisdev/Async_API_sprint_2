import sqlite3
from contextlib import contextmanager
from pathlib import Path

import psycopg2


@contextmanager
def create_sqlite_connection(
    database_path: Path,
):
    sqlite_connection = sqlite3.connect(
        database_path,
        detect_types=sqlite3.PARSE_COLNAMES,
    )
    sqlite_connection.row_factory = sqlite3.Row
    yield sqlite_connection
    sqlite_connection.close()


@contextmanager
def create_postgresql_connection(
    credentials: dict,
    cursor_class,
):
    pg_connection = psycopg2.connect(**credentials, cursor_factory=cursor_class)
    yield pg_connection
    pg_connection.close()
