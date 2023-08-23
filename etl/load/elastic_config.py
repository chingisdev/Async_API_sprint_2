from dataclasses import dataclass, field
from enum import Enum


class ElasticIndexName(Enum):
    GENRE = "genres"
    MOVIE = "movies"
    PERSON = "persons"


@dataclass(frozen=True)
class ElasticConfig:
    elastic_index: ElasticIndexName
    mapping: field(default_factory=dict)
    setting: field(default_factory=dict)


ELASTIC_GENRE_MAPPING = {
    "dynamic": "strict",
    "properties": {
        "id": {"type": "keyword"},
        "name": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "description": {
            "type": "text",
            "analyzer": "ru_en",
        },
    },
}

ELASTIC_PERSON_MAPPING = {
    "dynamic": "strict",
    "properties": {
        "id": {"type": "keyword"},
        "full_name": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "films": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "roles": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
            },
        },
    },
}

ELASTIC_MOVIE_MAPPING = {
    "dynamic": "strict",
    "properties": {
        "id": {"type": "keyword"},
        "imdb_rating": {"type": "float"},
        "genre": {"type": "keyword"},
        "title": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {"raw": {"type": "keyword"}},
        },
        "description": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "director": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "actors_names": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "writers_names": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "actors": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "name": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
            },
        },
        "writers": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "name": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
            },
        },
    },
}

ELASTIC_INDEX_SETTINGS = {
    "refresh_interval": "1s",
    "analysis": {
        "filter": {
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_",
            },
            "english_stemmer": {
                "type": "stemmer",
                "language": "english",
            },
            "english_possessive_stemmer": {
                "type": "stemmer",
                "language": "possessive_english",
            },
            "russian_stop": {
                "type": "stop",
                "stopwords": "_russian_",
            },
            "russian_stemmer": {
                "type": "stemmer",
                "language": "russian",
            },
        },
        "analyzer": {
            "ru_en": {
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "english_stop",
                    "english_stemmer",
                    "english_possessive_stemmer",
                    "russian_stop",
                    "russian_stemmer",
                ],
            }
        },
    },
}


ELASTIC_CONFIGS = [
    ElasticConfig(
        elastic_index=ElasticIndexName.MOVIE,
        mapping=ELASTIC_MOVIE_MAPPING,
        setting=ELASTIC_INDEX_SETTINGS,
    ),
    ElasticConfig(
        elastic_index=ElasticIndexName.GENRE,
        mapping=ELASTIC_GENRE_MAPPING,
        setting=ELASTIC_INDEX_SETTINGS,
    ),
    ElasticConfig(
        elastic_index=ElasticIndexName.PERSON,
        mapping=ELASTIC_PERSON_MAPPING,
        setting=ELASTIC_INDEX_SETTINGS,
    ),
]
