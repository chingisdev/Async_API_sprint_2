import uuid


def generate_single_film(film_id: str):
    return [
        {
            "id": film_id,
            "imdb_rating": 8.5,
            "genre": ["Action", "Sci-Fi"],
            "title": "The Star",
            "description": "New World",
            "director": ["Stan"],
            "actors": [{"id": "111", "name": "Ann"}, {"id": "222", "name": "Bob"}],
            "writers": [{"id": "333", "name": "Ben"}, {"id": "444", "name": "Howard"}],
        }
    ]


def generate_films(count: int):
    return [
        {
            "id": str(uuid.uuid4()),
            "imdb_rating": 8.5,
            "genre": ["Action", "Sci-Fi"],
            "title": "The Star",
            "description": "New World",
            "director": ["Stan"],
            "actors": [{"id": "111", "name": "Ann"}, {"id": "222", "name": "Bob"}],
            "writers": [{"id": "333", "name": "Ben"}, {"id": "444", "name": "Howard"}],
        }
        for _ in range(count)
    ]


def generate_single_genre(genre_id: str):
    return [
        {
            "id": genre_id,
            "name": "Horror",
            "description": "New World",
        }
    ]


def generate_genres(count: int, name: str, description: str):
    return [
        {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
        }
        for _ in range(count)
    ]


def generate_single_person(person_id: str):
    return [
        {
            "id": person_id,
            "full_name": "Bahrom",
            "films": [{"id": "1111", "roles": ["actor", "writer"]}, {"id": "2222", "roles": ["actor", "writer"]}],
        }
    ]


def generate_persons(count: int, full_name: str):
    return [
        {
            "id": str(uuid.uuid4()),
            "full_name": full_name,
            "films": [{"id": "1111", "roles": ["actor", "writer"]}, {"id": "2222", "roles": ["actor", "writer"]}],
        }
        for _ in range(count)
    ]
