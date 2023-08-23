from enum import Enum


class MoviesSortOptions(str, Enum):
    asc = "imdb_rating"
    desc = "-imdb_rating"
