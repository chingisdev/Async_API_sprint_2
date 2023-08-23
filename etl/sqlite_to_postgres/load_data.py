import logging
import os
import sqlite3
from pathlib import Path

from database_contexts import create_postgresql_connection, create_sqlite_connection
from dotenv import load_dotenv
from postgres_saver import PostgresSaver
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from sqlite_extractor import SQLiteExtractor


def load_from_sqlite(
    sqlite_connection: sqlite3.Connection,
    postgres_connection: _connection,
):
    try:
        postgres_saver = PostgresSaver(postgres_connection)
        sqlite_extractor = SQLiteExtractor(sqlite_connection)

        movies_tables = sqlite_extractor.extract_movies()
        postgres_saver.save_all_data(movies_tables)

    except IOError as e:
        logging.error(f"An IOError occurred {e}")


if __name__ == "__main__":
    load_dotenv()
    dsl = {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_HOST"),
        "port": int(os.environ.get("POSTGRES_PORT")),
    }
    BASE_DIR = Path(__file__).parent.absolute()
    SQLITE_DB_PATH = BASE_DIR / "db.sqlite"
    with create_sqlite_connection(SQLITE_DB_PATH) as sqlite_conn:
        with create_postgresql_connection(
            dsl,
            DictCursor,
        ) as pg_conn:
            load_from_sqlite(
                sqlite_conn,
                pg_conn,
            )
