import logging
from typing import List

from extract_transform.boundaries import DateBoundaries
from extract_transform.postgres_extractor import PostgresReceiver
from load.elastic_config import ElasticIndexName


class PostgresOrchester:
    def __init__(
        self,
        extractors: List[PostgresReceiver],
    ):
        self.extractors = extractors

    def extract_transformed_data(
        self,
        index: ElasticIndexName,
        table_names: List[str],
        boundaries: DateBoundaries,
    ):
        target_extractor = None
        for extractor in self.extractors:
            if extractor.index == index:
                target_extractor = extractor
                break
        if target_extractor is None:
            logging.info(
                "No target extractor for index %s",
                index.value,
            )
            return
        return target_extractor.get_transformed_ids(
            table_names,
            boundaries,
        )

    def extract_min_update_time(
        self,
    ):
        minimal_update_points = [extractor.get_minimal_update_time() for extractor in self.extractors]

        non_none_points = [point for point in minimal_update_points if point is not None]

        if not non_none_points:
            return None

        return min(non_none_points)
