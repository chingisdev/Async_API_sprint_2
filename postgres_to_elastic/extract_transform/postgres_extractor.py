from dataclasses import fields
from enum import Enum
from typing import Iterable, List, Optional

from load.elastic_config import ElasticIndexName
from sqlalchemy import create_engine, text
from time_event_decorators.backoff import backoff_public_methods

from .boundaries import DateBoundaries
from .query_manager import PostgresTableName, QueryManager


class IExtractor:
    def extract(
        self,
        table_names: List[str],
        boundaries: DateBoundaries,
    ) -> Iterable:
        pass


class ITransformer:
    def transform(self, ids) -> Iterable:
        pass


class TableQuery(Enum):
    TARGET = "target_table"
    RELATED = "related_table"
    TRANSFORM = "transform"
    GET_EARLIEST_UPDATE_TIME = "get_earliest"


@backoff_public_methods()
class PostgresReceiver(
    IExtractor,
    ITransformer,
):
    def __init__(
        self,
        index: ElasticIndexName,
        query_manager: QueryManager,
        schema,
        database_url,
        batch_size=100,
    ):
        self.index = index
        self.query_manager = query_manager
        self.schema = schema
        self.batch_size = batch_size
        self.engine = create_engine(database_url)

    def extract(
        self,
        table_names: List[PostgresTableName],
        boundaries: DateBoundaries,
    ) -> Iterable:
        unique_target_ids = set()
        for table_name in table_names:
            (query, params,) = self.query_manager.build_extract_query(
                table_name,
                from_time=boundaries.from_time,
                till_time=boundaries.till_time,
            )
            if not query or not params:
                continue
            ids = self._get_ids(
                query,
                params,
            )
            unique_target_ids.update(ids)
        return list(unique_target_ids)

    def transform(self, ids) -> Iterable:
        query = self.query_manager.get_transform_query()
        result = self._fetch_batching(
            query,
            ids,
        )
        return self._transform_to_schema(result)

    def _transform_to_schema(self, rows):
        schema_instances = []
        schema_fields = [f.name for f in fields(self.schema)]
        for row in rows:
            row_dict = {
                field_name: value
                for field_name, value in zip(
                    schema_fields,
                    row,
                )
            }
            schema_instances.append(row_dict)
        return schema_instances

    def _fetch_batching(
        self,
        query,
        to_batch,
    ):
        with self.engine.connect() as connection:
            all_rows = []
            offset = 0
            while True:
                batch = tuple(to_batch[offset : offset + self.batch_size])
                if not batch:
                    break
                params = {"ids": batch}
                statement = connection.execute(
                    text(query),
                    params,
                )
                rows = statement.fetchall()
                all_rows.extend(rows)
                offset += self.batch_size
            return all_rows

    def get_transformed_ids(
        self,
        table_names: List[PostgresTableName],
        boundaries: Optional[DateBoundaries],
    ):
        ids_to_transform = self.extract(
            table_names,
            boundaries,
        )
        transformed = self.transform(ids=ids_to_transform)
        return transformed

    def get_minimal_update_time(
        self,
    ):
        # query = self.table_queries[TableQuery.GET_EARLIEST_UPDATE_TIME]
        query = self.query_manager.get_earliest_update_query()
        with self.engine.connect() as connection:
            result = connection.execute(text(query)).fetchone()
            return result[0]

    def _get_ids(
        self,
        query,
        params: dict,
    ):
        rows = self._execute_sql_query(
            query,
            params,
        )
        return [row[0] for row in rows]

    def _fetch_many(self, cursor) -> list:
        data = []
        while batch := cursor.fetchmany(self.batch_size):
            data.extend(batch)
        return data

    def _execute_sql_query(
        self,
        query: str,
        params: dict,
    ):
        with self.engine.connect() as connection:
            data = []
            result = connection.execution_options(stream_results=True).execute(
                text(query),
                params,
            )
            while batch := result.fetchmany(self.batch_size):
                data.extend(batch)
            return data
