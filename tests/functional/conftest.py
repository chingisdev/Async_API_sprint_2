import urllib
from typing import List

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from .settings import test_settings


def get_es_actions(data: List[dict], index: str):
    return [{"_index": index, "_source": doc, "_id": doc["id"]} for doc in data]


@pytest.fixture
async def es_client():
    client = AsyncElasticsearch(hosts=test_settings.elastic_url)
    yield client
    await client.close()


@pytest.fixture
def es_write_data(es_client):
    async def inner(data: List[dict], es_index: str):
        actions = get_es_actions(data, es_index)
        _es_client = (item async for item in es_client)
        async for client in es_client:
            client: AsyncElasticsearch
            index_exists = await client.indices.exists(index=es_index)
            if index_exists:
                await client.indices.delete(index=es_index)

            if test_settings.es_maps.get(es_index) is None:
                raise Exception(f"Mapping for index '{es_index}' not found")

            await client.indices.create(
                index=es_index, mappings=test_settings.es_maps.get(es_index), settings=test_settings.es_index_mapping
            )

            await async_bulk(client, actions)

            await client.indices.refresh(index=es_index)

    return inner


@pytest.fixture
def make_get_request():
    async def inner(endpoint: str, params: dict = None):
        url = test_settings.service_url + endpoint

        if params:
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            url = f"{url}?{encoded_params}"
        aiohttp_client = aiohttp.ClientSession()

        try:
            async with aiohttp_client.get(url) as response:
                body = await response.json()
                status = response.status

            return status, body
        finally:
            await aiohttp_client.close()

    return inner
