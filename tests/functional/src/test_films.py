from http import HTTPStatus

import pytest

from tests.functional.testdata.data_generator import (
    generate_films,
    generate_single_film,
)

INDEX = "movies"


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [({"film_id": "accb643b-db2c-4f5b-b59b-e9727bb5e859"}, {"status": HTTPStatus.OK})],
)
async def test_get_film(make_get_request, es_write_data, search_data: dict, expected_answer: dict):
    es_data = generate_single_film(search_data.get("film_id"))
    await es_write_data(es_data, INDEX)

    status, body = await make_get_request("/api/v1/films/" + search_data.get("film_id"))

    assert status == expected_answer["status"]


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [({"film_id": "accb643b-db2c-4f5b-b59b-e9727bb5e839"}, {"status": HTTPStatus.NOT_FOUND})],
)
async def test_get_film_not_exists(make_get_request, search_data: dict, expected_answer: dict):
    status, body = await make_get_request("/api/v1/films/" + search_data.get("film_id"))
    assert status == expected_answer["status"]


async def test_write_films_to_elastic(es_write_data):
    """Done this test to prevent rewriting same data multiple times"""
    es_data = generate_films(60)
    await es_write_data(es_data, INDEX)


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"search": "The Star"}, {"status": HTTPStatus.OK, "length": 50}),
        ({"search": "Mashed potato"}, {"status": HTTPStatus.OK, "length": 0}),
    ],
)
async def test_search_film(make_get_request, search_data: dict, expected_answer: dict):
    status, body = await make_get_request("/api/v1/films/search", search_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [({"search_1": "Mashed potato", "page_size": "2d"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY})],
)
async def test_search_film_invalid_params(make_get_request, search_data: dict, expected_answer: dict):
    status, body = await make_get_request("/api/v1/films/search", search_data)
    assert status == expected_answer["status"]
