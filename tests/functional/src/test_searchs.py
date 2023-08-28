import uuid

import pytest


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"search": "The Star"}, {"status": 200, "length": 50}),
        ({"search": "Mashed potato"}, {"status": 200, "length": 0}),
    ],
)
@pytest.mark.asyncio
async def test_search_film(make_get_request, es_write_data, search_data: dict, expected_answer: dict):
    es_data = [
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
        for _ in range(60)
    ]

    await es_write_data(es_data, "movies")

    status, body = await make_get_request("/api/v1/films/search", search_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"search": "horror"}, {"status": 200, "length": 24}),
        ({"search": "Mashed potato"}, {"status": 200, "length": 0}),
    ],
)
@pytest.mark.asyncio
async def test_search_genres(make_get_request, es_write_data, search_data: dict, expected_answer: dict):
    es_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Horror",
            "description": "New World",
        }
        for _ in range(24)
    ]

    await es_write_data(es_data, "genres")

    status, body = await make_get_request("/api/v1/genres/search", search_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"search": "Bahrom"}, {"status": 200, "length": 32}),
        ({"search": "barom"}, {"status": 200, "length": 32}),
        ({"search": "Ban"}, {"status": 200, "length": 0}),
    ],
)
@pytest.mark.asyncio
async def test_search_persons(make_get_request, es_write_data, search_data: dict, expected_answer: dict):
    es_data = [
        {
            "id": str(uuid.uuid4()),
            "full_name": "Bahrom",
            "films": [{"id": "1111", "roles": ["actor", "writer"]}, {"id": "2222", "roles": ["actor", "writer"]}],
        }
        for _ in range(32)
    ]

    await es_write_data(es_data, "persons")

    status, body = await make_get_request("/api/v1/persons/search", search_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]
