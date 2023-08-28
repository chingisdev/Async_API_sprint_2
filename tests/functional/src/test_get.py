import pytest


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"film_id": "accb643b-db2c-4f5b-b59b-e9727bb5e859"}, {"status": 200}),
        ({"film_id": "0000000-0000-000000-000000"}, {"status": 404}),
    ],
)
@pytest.mark.asyncio
async def test_get_film(make_get_request, es_write_data, search_data: dict, expected_answer: dict):
    es_data = [
        {
            "id": "accb643b-db2c-4f5b-b59b-e9727bb5e859",
            "imdb_rating": 8.5,
            "genre": ["Action", "Sci-Fi"],
            "title": "The Star",
            "description": "New World",
            "director": ["Stan"],
            "actors": [{"id": "111", "name": "Ann"}, {"id": "222", "name": "Bob"}],
            "writers": [{"id": "333", "name": "Ben"}, {"id": "444", "name": "Howard"}],
        }
    ]

    await es_write_data(es_data, "movies")

    status, body = await make_get_request("/api/v1/films/" + search_data.get("film_id"))

    assert status == expected_answer["status"]


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"genre_id": "145acdf0-d0ff-4bac-8169-2dac732290f5"}, {"status": 200}),
        ({"genre_id": "0000000-0000-000000-000000"}, {"status": 404}),
    ],
)
@pytest.mark.asyncio
async def test_get_genres(make_get_request, es_write_data, search_data: dict, expected_answer: dict):
    es_data = [
        {
            "id": "145acdf0-d0ff-4bac-8169-2dac732290f5",
            "name": "Horror",
            "description": "New World",
        }
    ]

    await es_write_data(es_data, "genres")

    status, body = await make_get_request("/api/v1/genres/" + search_data.get("genre_id"))

    assert status == expected_answer["status"]


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"person_id": "5c332d8a-4691-41bd-b5c8-028018a17461"}, {"status": 200}),
        ({"person_id": "0000000-0000-000000-000000"}, {"status": 404}),
    ],
)
@pytest.mark.asyncio
async def test_get_persons(make_get_request, es_write_data, search_data: dict, expected_answer: dict):
    es_data = [
        {
            "id": "5c332d8a-4691-41bd-b5c8-028018a17461",
            "full_name": "Bahrom",
            "films": [{"id": "1111", "roles": ["actor", "writer"]}, {"id": "2222", "roles": ["actor", "writer"]}],
        }
    ]

    await es_write_data(es_data, "persons")

    status, body = await make_get_request("/api/v1/persons/" + search_data.get("person_id"))

    assert status == expected_answer["status"]
