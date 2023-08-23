import orjson
from pydantic import BaseModel

from .genre import MovieGenre
from .person import MoviePerson, MoviePersonName


class Film(BaseModel):
    """
    Represents a film.

    Attributes:
    - id (UUID): Unique identifier
    - title (str): The title of the film.
    - description (Optional[str]): The description of the film (if available).
    - imdb_rating (Optional[str]): The rating of the film (if available).
    - actors (Optional[List[Person]]): List of actors associated with the film (if available).
    - writers (Optional[List[Person]]): List of writers associated with the film (if available).
    - directors (Optional[List[Person]]): List of directors associated with the film (if available).
    - genres (Optional[List[Genre]]): List of genres associated with the film (if available).
    """

    id: str
    title: str
    description: str | None
    imdb_rating: float | None
    actors: list[MoviePerson] | None
    writers: list[MoviePerson] | None
    directors: list[MoviePersonName] | None
    genres: list[MovieGenre] | None

    @staticmethod
    def parse_from_elastic(
        document,
    ):
        return Film(
            id=document["_source"]["id"],
            title=document["_source"]["title"],
            description=document["_source"]["description"],
            imdb_rating=document["_source"]["imdb_rating"],
            actors=[
                MoviePerson(
                    id=person["id"],
                    full_name=person["name"],
                )
                for person in document["_source"]["actors"]
            ],
            writers=[
                MoviePerson(
                    id=person["id"],
                    full_name=person["name"],
                )
                for person in document["_source"]["writers"]
            ],
            directors=[
                MoviePersonName(full_name=director_name)
                for director_name in document["_source"]["director"]
                if director_name is not None
            ],
            genres=[MovieGenre(name=genre_name) for genre_name in document["_source"]["genre"]],
        )

    @staticmethod
    def parse_from_redis(
        film_str: str,
    ):
        film = orjson.loads(film_str)

        return Film(
            id=film["id"],
            title=film["title"],
            description=film["description"],
            imdb_rating=film["imdb_rating"],
            actors=[
                MoviePerson(
                    id=person["id"],
                    full_name=person["full_name"],
                )
                for person in film["actors"]
                if person is not None
            ],
            writers=[
                MoviePerson(
                    id=person["id"],
                    full_name=person["full_name"],
                )
                for person in film["writers"]
                if person is not None
            ],
            directors=[
                MoviePersonName(full_name=director["full_name"])
                for director in film["directors"]
                if director is not None
            ],
            genres=[MovieGenre(name=genre["name"]) for genre in film["genres"] if genre is not None],
        )
