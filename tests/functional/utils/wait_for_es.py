import time

from elasticsearch import Elasticsearch
from functional.settings import test_settings

if __name__ == "__main__":
    es_client = Elasticsearch(hosts=test_settings.elastic_url)
    while True:
        if es_client.ping():
            break
        time.sleep(1)
