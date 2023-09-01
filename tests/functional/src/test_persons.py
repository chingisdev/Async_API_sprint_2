from http import HTTPStatus

import pytest

from tests.functional.testdata.data_generator import (
    generate_persons,
    generate_single_person,
)

INDEX = "persons"


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [({"person_id": "accb643b-db2c-4f5b-b59b-e9727bb5e859"}, {"status": HTTPStatus.OK})],
)
async def test_get_person(make_get_request, es_write_data, search_data: dict, expected_answer: dict):
    es_data = generate_single_person(search_data.get("person_id"))
    await es_write_data(es_data, INDEX)

    status, body = await make_get_request("/api/v1/persons/" + search_data.get("person_id"))

    assert status == expected_answer["status"]


async def tests_write_persons(es_write_data):
    es_data = generate_persons(32, "Bahrom")
    await es_write_data(es_data, INDEX)


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"search": "Bahrom"}, {"status": HTTPStatus.OK, "length": 32}),
        ({"search": "barom"}, {"status": HTTPStatus.OK, "length": 32}),
        ({"search": "Ban"}, {"status": HTTPStatus.OK, "length": 0}),
    ],
)
async def test_search_person(make_get_request, search_data: dict, expected_answer: dict):
    status, body = await make_get_request("/api/v1/persons/search", search_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [({"person_id": "accb643b-db2c-4f5b-b59b-e9727bb5e839"}, {"status": HTTPStatus.NOT_FOUND})],
)
async def test_get_person_not_exists(make_get_request, search_data: dict, expected_answer: dict):
    status, body = await make_get_request("/api/v1/persons/" + search_data.get("person_id"))
    assert status == expected_answer["status"]


@pytest.mark.parametrize(
    "search_data, expected_answer",
    [
        ({"search": "Mashed Bahrom", "page_size": "2d"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
async def test_search_person_invalid_params(make_get_request, search_data: dict, expected_answer: dict):
    status, body = await make_get_request("/api/v1/persons/search", search_data)
    assert status == expected_answer["status"]
