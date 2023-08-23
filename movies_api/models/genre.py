from pydantic import BaseModel


class MovieGenre(BaseModel):
    """
    Represents a genre associated with a film

    Attributes:
        - name (str): The name of genre
    """

    name: str


class Genre(BaseModel):
    """
    Represents a genre associated with a film

    Attributes:
        - id (str): Unique identifier
        - name (str): The name of genre
        - description (str): The description of genre (if available)
    """

    id: str
    name: str
    description: str | None
