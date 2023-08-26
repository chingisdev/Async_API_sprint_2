import urllib
from typing import List

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from .settings import test_settings


def get_es_actions(data: List[dict], index: str):
    return [{"_index": index, "_source": doc} for doc in data]


@pytest.fixture(scope="session")
async def aiohttp_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="session")
async def es_client():
    client = AsyncElasticsearch(hosts=test_settings.elastic_url)
    yield client
    await client.close()


@pytest.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: List[dict], es_index):
        actions = get_es_actions(data, es_index)

        # Looking for index
        index_exists = await es_client.indices.exists(index=es_index)

        if index_exists:
            await es_client.indices.delete(index=es_index)

        if test_settings.es_maps.get(es_index) is None:
            raise Exception("Mapping for index <<%s>> not Found ", es_index)

        await es_client.indices.create(
            index=es_index, mappings=test_settings.es_mapps.get(es_index), settings=test_settings.es_index_mapping
        )

        await async_bulk(es_client, actions)
        await es_client.close()

    return inner


@pytest.fixture
async def make_get_request(aiohttp_client: aiohttp.ClientSession):
    async def inner(endpoint: str, params: dict):
        base_url = test_settings.service_url + endpoint
        encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

        url = f"{base_url}?{encoded_params}"

        async with aiohttp_client.get(url) as response:
            body = await response.json()
            status = response.status

        return status, body

    return inner
