import pytest

from tests.functional.testdata.data_generator import (
    generate_films,
    generate_genres,
    generate_persons,
)


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"search": "The Star"}, {"status": 200, "length": 50}),
        ({"search": "Mashed potato"}, {"status": 200, "length": 0}),
    ],
)
@pytest.mark.asyncio
async def test_search_film(make_get_request, es_write_data, search_data: dict, expected_answer: dict):
    es_data = generate_films(60)

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
    es_data = generate_genres(24, "Horror", "Scaring movies collection")

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
    es_data = generate_persons(32, "Bahrom")

    await es_write_data(es_data, "persons")

    status, body = await make_get_request("/api/v1/persons/search", search_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]
