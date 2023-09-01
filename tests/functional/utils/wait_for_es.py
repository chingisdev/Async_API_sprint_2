from elasticsearch import Elasticsearch
from functional.settings import test_settings
from functional.utils.backoff import backoff


@backoff()
def wait_for_es():
    es_client = Elasticsearch(hosts=test_settings.elastic_url)
    if es_client.ping():
        return
    raise Exception("Elasticsearch is not ready...")


if __name__ == "__main__":
    wait_for_es()
