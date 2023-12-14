from abc import ABC, abstractmethod
from typing import Callable, Generic, List, Optional, Type, TypeVar

from backoff.backoff import backoff_public_methods
from elasticsearch import NotFoundError
from pydantic import BaseModel
from search_engine.search_engine_protocol import SearchEngineProtocol

T = TypeVar("T", bound=BaseModel)


class AbstractSearchService(ABC, Generic[T]):
    def __init__(self, search_engine: SearchEngineProtocol, index: str, deserialize: Callable[[dict], T]):
        self.search_engine = search_engine
        self.index = index
        self._deserialize = deserialize

    @abstractmethod
    async def get_by_id(self, instance_id: str) -> Optional[T]:
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    async def get_by_parameters(
        self, page_number: int, page_size: int, search: str | None = None, sort: str | None = None
    ) -> Optional[List[T]]:
        raise NotImplementedError("Subclasses must implement this method")


@backoff_public_methods()
class ElasticSearchService(AbstractSearchService[T]):
    async def get_by_id(self, instance_id: str) -> Optional[T]:
        try:
            doc = await self.search_engine.get(index=self.index, id=instance_id)
            return self._deserialize(doc)
        except NotFoundError:
            return None

    async def get_by_parameters(
        self, page_number: int, page_size: int, search: str | None = None, sort: str | None = None
    ) -> Optional[List[T]]:
        query = {
            "query": self._get_query_match(search=search),
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }

        if sort:
            query["sort"] = self._get_sort_params(sort=sort)

        try:
            doc = await self.search_engine.search(
                index=self.index,
                body=query,
            )
        except NotFoundError:
            return None
        documents = doc["hits"]["hits"]
        return [self._deserialize(doc) for doc in documents]

    @staticmethod
    def _get_sort_params(sort):
        (sort_key, sort_order,) = (
            (sort[1:], "desc") if sort.startswith("-") else (sort, "asc")
        )
        return [{sort_key: sort_order}]

    @staticmethod
    def _get_query_match(search: str | None):
        if search:
            return {
                "multi_match": {
                    "query": search,
                    "fields": ["*"],
                    "fuzziness": "AUTO",
                }
            }
        return {"match_all": {}}


def automatic_search_deserializer(model: Type[BaseModel], data: dict):
    return model.model_validate(data["_source"])
