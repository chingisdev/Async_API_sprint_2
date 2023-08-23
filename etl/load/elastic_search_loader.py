import logging
from typing import Optional

from elasticsearch import Elasticsearch, helpers
from load.elastic_config import ElasticConfig, ElasticIndexName
from time_event_decorators.backoff import backoff_public_methods


@backoff_public_methods()
class ElasticLoader:
    def __init__(
        self,
        es_configs: list[ElasticConfig],
        es_indexes: list[ElasticIndexName],
        es_url: str,
    ) -> None:
        """
        Initialize the ElasticsearchLoader.

        :param es_indexes: The names of the Elasticsearch indexes to use.
        :param mappings: Optional mappings for the Elasticsearch index. Default is None.
        :param settings: Optional settings for the Elasticsearch index. Default is None.
        """
        self.es = Elasticsearch(es_url)
        self.es_indexes = es_indexes
        self.es_configs = es_configs
        self.create_indexes()

    def load_data_to_es(
        self,
        es_data: Optional[list],
        es_index: ElasticIndexName,
    ):
        """
        Loads data to ElasticSearch.

        :return: None
        """

        if es_index not in self.es_indexes:
            logging.error("You are trying to load data to non existing index: %s".format(es_index))
            return
        if es_data is None:
            logging.info("You passed empty data to load to: %s".format(es_index))
            return
        actions = ElasticLoader.transform_data_to_actions(
            es_data,
            es_index,
        )
        helpers.bulk(
            self.es,
            actions,
        )

    def create_indexes(
        self,
    ):
        for elastic_configuration in self.es_configs:
            if self.has_index(elastic_configuration.elastic_index.value):
                continue
            self.es.indices.create(
                index=elastic_configuration.elastic_index.value,
                mappings=elastic_configuration.mapping,
                settings=elastic_configuration.setting,
            )

    def has_index(
        self,
        es_index,
    ) -> bool:
        """
        Check if the Elasticsearch index exists.

        :return: True if the index exists, False otherwise.
        """
        return self.es.indices.exists(index=es_index).body

    @staticmethod
    def transform_data_to_actions(
        data: Optional[list],
        index: ElasticIndexName,
    ):
        return [
            {
                "_index": index.value,
                "_id": doc["id"],
                "_source": doc,
            }
            for doc in data
        ]
