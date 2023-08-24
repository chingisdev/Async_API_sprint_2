import sqlite3

from models import FilmWork, Genre, GenreFilmwork, Person, PersonFilmwork


class SQLiteExtractor:
    def __init__(
        self,
        sqlite_connection: sqlite3.Connection,
    ):
        self.connection = sqlite_connection
        self.fetch_size = 100
        self.table_map = {
            "film_work": FilmWork,
            "genre": Genre,
            "person": Person,
            "person_film_work": PersonFilmwork,
            "genre_film_work": GenreFilmwork,
        }
        self.cursor = self.connection.cursor()

    def extract_movies(
        self,
    ):
        movies = {}
        for (
            table_name,
            model,
        ) in self.table_map.items():
            movies[table_name] = self._execute_select_query(
                table_name,
                model,
            )
        return movies

    def _execute_select_query(
        self,
        table_name,
        model_class,
    ):
        self.cursor.execute(f"SELECT * FROM {table_name};")
        batches: list[model_class] = []
        while data := self.cursor.fetchmany(self.fetch_size):
            converted_data = [model_class(**dict(movie)) for movie in data]
            batches.extend(converted_data)
        return batches
