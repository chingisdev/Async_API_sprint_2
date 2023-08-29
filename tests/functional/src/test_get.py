import pytest
from functional.testdata.data_generator import (
    generate_single_film,
    generate_single_genre,
    generate_single_person,
)


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"film_id": "accb643b-db2c-4f5b-b59b-e9727bb5e859"}, {"status": 200}),
        ({"film_id": "0000000-0000-000000-000000"}, {"status": 404}),
    ],
)
@pytest.mark.asyncio
async def test_get_film(make_get_request, es_write_data, search_data: dict, expected_answer: dict):
    es_data = generate_single_film(search_data.get("film_id"))

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
    es_data = generate_single_genre(search_data.get("genre_id"))

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
    es_data = generate_single_person(search_data.get("person_id"))

    await es_write_data(es_data, "persons")

    status, body = await make_get_request("/api/v1/persons/" + search_data.get("person_id"))

    assert status == expected_answer["status"]
