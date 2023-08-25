from typing import Generic, List, Optional, TypeVar

from backoff.backoff import backoff_public_methods
from elasticsearch import NotFoundError
from models.film import Film
from models.genre import Genre
from models.person import Person
from pydantic import BaseModel
from search_engine.search_engine_protocol import SearchEngineProtocol

T = TypeVar("T", bound=BaseModel)


@backoff_public_methods()
class SearchService(Generic[T]):
    def __init__(self, search_engine: SearchEngineProtocol, index: str):
        self.search_engine = search_engine
        self.index = index

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

    def _deserialize(self, data):
        raise NotImplementedError("Subclasses must implement this method")


class FilmSearchService(SearchService[Film]):
    def _deserialize(self, data):
        return Film.deserialize_search(data)


class GenreSearchService(SearchService[Genre]):
    def _deserialize(self, data):
        return Genre.model_validate(data["_source"])


class PersonSearchService(SearchService[Person]):
    def _deserialize(self, data):
        return Person.model_validate(data["_source"])
