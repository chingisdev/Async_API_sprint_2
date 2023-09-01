from http import HTTPStatus

import pytest

from tests.functional.testdata.data_generator import (
    generate_genres,
    generate_single_genre,
)

INDEX = "genres"


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [({"genre_id": "accb643b-db2c-4f5b-b59b-e9727bb5e859"}, {"status": HTTPStatus.OK})],
)
async def test_get_single_genre(make_get_request, es_write_data, search_data: dict, expected_answer: dict):
    es_data = generate_single_genre(search_data.get("genre_id"))
    await es_write_data(es_data, INDEX)

    status, body = await make_get_request("/api/v1/genres/" + search_data.get("genre_id"))

    assert status == expected_answer["status"]


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [({"genre_id": "accb643b-db2c-4f5b-b59b-e9727bb5e839"}, {"status": HTTPStatus.NOT_FOUND})],
)
async def test_get_genre_not_exists(make_get_request, search_data: dict, expected_answer: dict):
    status, body = await make_get_request("/api/v1/genres/" + search_data.get("genre_id"))
    assert status == expected_answer["status"]


async def test_write_genres_to_elastic(es_write_data):
    """Done this test to prevent rewriting same data multiple times"""
    es_data = generate_genres(24, "Horror", "Scaring movies collection")
    await es_write_data(es_data, INDEX)


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"search": "horror"}, {"status": 200, "length": 24}),
        ({"search": "Mashed potato"}, {"status": 200, "length": 0}),
    ],
)
async def test_search_genre(make_get_request, search_data: dict, expected_answer: dict):
    status, body = await make_get_request("/api/v1/genres/search", search_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [({"search": "horror", "page_size": "2d"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY})],
)
async def test_search_genre_invalid_params(make_get_request, search_data: dict, expected_answer: dict):
    status, body = await make_get_request("/api/v1/genres/search", search_data)
    assert status == expected_answer["status"]
