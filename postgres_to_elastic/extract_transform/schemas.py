from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class FilmWork:
    id: UUID
    title: str
    description: str
    imdb_rating: str
    actors_names: list[str] = field(default_factory=list)
    writers_names: list[str] = field(default_factory=list)
    director: list[str] = field(default_factory=list)
    genre: list[str] = field(default_factory=list)
    actors: list[dict] = field(default_factory=list)
    writers: list[dict] = field(default_factory=list)


@dataclass
class Genre:
    id: UUID
    name: str
    description: str


@dataclass
class Person:
    id: UUID
    full_name: str
    films: list[dict] = field(default_factory=list)
