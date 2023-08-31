from abc import ABC, abstractmethod
from typing import Callable, Generic, List, Optional, Type, TypeVar

from elasticsearch import NotFoundError
from pydantic import BaseModel
from search_engine.search_engine_protocol import SearchEngineProtocol

T = TypeVar("T", bound=BaseModel)


class AbstractSearchService(ABC, Generic[T]):
    def __init__(self, search_engine: SearchEngineProtocol, index: str, deserialize: Callable[[dict], T]):
        self.search_engine = search_engine
        self.index = index
        self.deserialize = deserialize

    @abstractmethod
    async def get_by_id(self, instance_id: str) -> Optional[T]:
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    async def get_by_parameters(
        self, page_number: int, page_size: int, search: str | None = None, sort: str | None = None
    ) -> Optional[List[T]]:
        raise NotImplementedError("Subclasses must implement this method")


class ElasticSearchService(AbstractSearchService[T]):
    async def get_by_id(self, instance_id: str) -> Optional[T]:
        try:
            doc = await self.search_engine.get(index=self.index, id=instance_id)
            return self.deserialize(doc)
        except NotFoundError:
            return None

    async def get_by_parameters(
        self, page_number: int, page_size: int, search: str | None = None, sort: str | None = None
    ) -> Optional[List[T]]:
        query = {
            "query": {
                "multi_match": {
                    "query": search,
                    "fields": ["*"],
                    "fuzziness": "AUTO",
                }
            }
            if search
            else {"match_all": {}},
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }

        if sort:
            (sort_key, sort_order,) = (
                (sort[1:], "desc") if sort.startswith("-") else (sort, "asc")
            )
            query["sort"] = [{sort_key: sort_order}]

        try:
            doc = await self.search_engine.search(
                index=self.index,
                body=query,
            )
        except NotFoundError:
            return None
        documents = doc["hits"]["hits"]
        return [self.deserialize(doc) for doc in documents]


def auto_deserializer(model: Type[BaseModel], data: dict):
    return model.model_validate(data["_source"])
