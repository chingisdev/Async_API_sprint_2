from typing import List

import pytest
from elasticsearch import AsyncElasticsearch

from .settings import test_settings


@pytest.fixture(scope="session")
async def es_client():
    client = AsyncElasticsearch(hosts=test_settings.elastic_url)
    yield client
    await client.close()


@pytest.fixture
def es_write_data(es_client):
    async def inner(data: List[dict]):
        bulk_query = get_es_bulk_query(data, test_settings.es_index, test_settings.es_id_field)
        str_query = "\n".join(bulk_query) + "\n"

        response = await es_client.bulk(str_query, refresh=True)
        await es_client.close()
        if response["errors"]:
            raise Exception("Ошибка записи данных в Elasticsearch")

    return inner
