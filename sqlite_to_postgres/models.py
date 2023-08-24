import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class FilmWork:
    id: uuid.UUID
    title: str
    description: str
    creation_date: field(default_factory=datetime)
    file_path: str
    rating: float
    type: str
    created_at: field(default_factory=datetime)
    updated_at: field(default_factory=datetime)

    def __post_init__(
        self,
    ):
        date_format = "%Y-%m-%d %H:%M:%S.%f+00"
        if isinstance(
            self.created_at,
            str,
        ):
            self.created_at = datetime.strptime(
                self.created_at,
                date_format,
            ).replace(tzinfo=timezone.utc)
        if isinstance(
            self.updated_at,
            str,
        ):
            self.updated_at = datetime.strptime(
                self.updated_at,
                date_format,
            ).replace(tzinfo=timezone.utc)


@dataclass
class Genre:
    id: uuid.UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(
        self,
    ):
        date_format = "%Y-%m-%d %H:%M:%S.%f+00"
        if isinstance(
            self.created_at,
            str,
        ):
            self.created_at = datetime.strptime(
                self.created_at,
                date_format,
            ).replace(tzinfo=timezone.utc)
        if isinstance(
            self.updated_at,
            str,
        ):
            self.updated_at = datetime.strptime(
                self.updated_at,
                date_format,
            ).replace(tzinfo=timezone.utc)


@dataclass
class Person:
    id: uuid.UUID
    full_name: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(
        self,
    ):
        date_format = "%Y-%m-%d %H:%M:%S.%f+00"
        if isinstance(
            self.created_at,
            str,
        ):
            self.created_at = datetime.strptime(
                self.created_at,
                date_format,
            ).replace(tzinfo=timezone.utc)
        if isinstance(
            self.updated_at,
            str,
        ):
            self.updated_at = datetime.strptime(
                self.updated_at,
                date_format,
            ).replace(tzinfo=timezone.utc)


@dataclass
class GenreFilmwork:
    id: uuid.UUID
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime

    def __post_init__(
        self,
    ):
        date_format = "%Y-%m-%d %H:%M:%S.%f+00"
        if isinstance(
            self.created_at,
            str,
        ):
            self.created_at = datetime.strptime(
                self.created_at,
                date_format,
            ).replace(tzinfo=timezone.utc)


@dataclass
class PersonFilmwork:
    id: uuid.UUID
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime

    def __post_init__(
        self,
    ):
        date_format = "%Y-%m-%d %H:%M:%S.%f+00"
        if isinstance(
            self.created_at,
            str,
        ):
            self.created_at = datetime.strptime(
                self.created_at,
                date_format,
            ).replace(tzinfo=timezone.utc)
