import urllib
from typing import List

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings


def get_es_actions(data: List[dict], index: str) -> list[dict]:
    return [{"_index": index, "_source": doc, "_id": doc["id"]} for doc in data]


@pytest.fixture
def es_write_data(client_elastic: AsyncElasticsearch):
    async def _inner(data: List[dict], es_index: str):
        actions = get_es_actions(data, es_index)

        index_exists = await client_elastic.indices.exists(index=es_index)
        if index_exists:
            await client_elastic.indices.delete(index=es_index)

        if test_settings.es_maps.get(es_index) is None:
            raise Exception(f"Mapping for index '{es_index}' not found")

        await client_elastic.indices.create(
            index=es_index, mappings=test_settings.es_maps.get(es_index), settings=test_settings.es_index_mapping
        )

        await async_bulk(client_elastic, actions)

        await client_elastic.indices.refresh(index=es_index)

    return _inner


@pytest.fixture
def make_get_request(aiohttp_client: aiohttp.ClientSession):
    async def _inner(endpoint: str, params: dict = None):
        url = test_settings.service_url + endpoint

        if params:
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            url = f"{url}?{encoded_params}"

        async with aiohttp_client.get(url) as response:
            body = await response.json()
            status = response.status
        return status, body

    return _inner
