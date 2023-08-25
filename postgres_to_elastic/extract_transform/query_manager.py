from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from .query_builder import BaseQueryBuilder


class TableQuery(Enum):
    TARGET = "target_table"
    RELATED = "related_table"
    TRANSFORM = "transform"
    GET_EARLIEST_UPDATE_TIME = "get_earliest"


class PostgresTableName(Enum):
    FILM_WORK = "content.film_work"
    GENRE = "content.genre"
    PERSON = "content.person"


@dataclass
class IntermediateTable:
    table_name: str
    main_id_field: str
    related_id_field: str

    @property
    def relative_id(
        self,
    ):
        return f"{self.related_id_field}"

    @property
    def base_id(
        self,
    ):
        return f"{self.main_id_field}"


class QueryManager:
    def __init__(
        self,
        base_table: PostgresTableName,
        queries: Dict[
            str,
            BaseQueryBuilder,
        ],
        relative_tables: Optional[
            Dict[
                str,
                Optional[IntermediateTable],
            ]
        ],
    ):
        self.base_table = base_table
        self.queries = queries
        self.relative_tables = relative_tables

    def build_extract_query(
        self,
        table_name: PostgresTableName,
        **kwargs,
    ):
        if self.base_table == table_name:
            query = self.queries[TableQuery.TARGET.value].build_query()
            query = query.format(base_table=table_name.value)
            return (
                query,
                kwargs,
            )

        if self.relative_tables and self.relative_tables.get(table_name.value):
            relative_table = self.relative_tables.get(table_name.value)
            query = self.queries[TableQuery.RELATED.value].build_query()
            query = query.format(
                base_table=self.base_table.value,
                relative_table=table_name.value,
                relative_m2m_table=relative_table.table_name,
                relative_id=relative_table.relative_id,
                base_id=relative_table.base_id,
            )
            return (
                query,
                kwargs,
            )
        return (
            None,
            None,
        )

    def get_earliest_update_query(
        self,
    ) -> str:
        query = self.queries[TableQuery.GET_EARLIEST_UPDATE_TIME.value].build_query()
        query = query.format(self.base_table.value)
        return query

    def get_transform_query(
        self,
    ) -> str:
        query = self.queries[TableQuery.TRANSFORM.value].build_query()
        return query
