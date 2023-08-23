from pydantic import BaseModel


class PersonFilms(BaseModel):
    """
    Attributes:
        - id (str):
        - roles (List[str | None]):
    """

    id: str
    roles: list[str | None] = []


class MoviePerson(BaseModel):
    """
    Represents a person associated with a film.

    Attributes:
    - id (Str): Unique identifier.
    - full_name (str): The name of the person.
    """

    id: str
    full_name: str


class MoviePersonName(BaseModel):
    """
    Represents a short version of person associated with a film.

    Attributes:
    - full_name (str): The full_name of the person.
    """

    full_name: str


class Person(BaseModel):
    """
    Represents a person associated with a film.

    Attributes:
    - id (UUID): Unique identifier
    - full_name (str): The full_name of the person.
    - films (Optional[List[PersonFilms]]): List of films associated with the film (if available).

    """

    id: str
    full_name: str
    films: list["PersonFilms"] | None
