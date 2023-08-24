from functools import lru_cache
from typing import List, Optional

import orjson
from cache_storage.cache_storage_protocol import CacheStorageProtocol
from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import NotFoundError
from fastapi import Depends
from models.person import Person
from search_engine.search_engine_protocol import SearchEngineProtocol


class PersonService:
    index = "persons"
    redis_prefix_single = "person"
    redis_prefix_plural = "persons"

    def __init__(
        self,
        redis: CacheStorageProtocol,
        elastic: SearchEngineProtocol,
    ):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._get_from_cache(person_id)
        if not person:
            person = await self._get_from_elastic(person_id)
            if not person:
                return None
            await self._put_instance_to_cache(person)

        return person

    async def get_by_parameters(
        self,
        page_number: int,
        page_size: int,
        search: str | None,
        sort: str | None = None,
    ) -> list[Optional[Person]]:
        persons = await self._get_list_from_cache(
            search=search,
            page_size=page_size,
            page_number=page_number,
            sort=sort,
        )
        if not persons:
            persons = await self._get_list_from_elastic(
                search=search,
                page_number=page_number,
                page_size=page_size,
                sort=sort,
            )
            if not persons:
                return []
            await self._put_list_to_cache(
                page_number=page_number,
                page_size=page_size,
                sort=sort,
                persons=persons,
            )

        return persons

    async def _get_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(
                index=self.index,
                id=person_id,
            )
            return Person(**doc["_source"])
        except NotFoundError:
            return None

    async def _get_list_from_elastic(
        self,
        page_number: int,
        page_size: int,
        search: str | None,
        sort: str | None = None,
    ):
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
            doc = await self.elastic.search(
                index=self.index,
                body=query,
            )
        except NotFoundError:
            return None
        documents = doc["hits"]["hits"]
        persons = [Person.model_validate(doc["_source"]) for doc in documents]
        return persons

    async def _get_from_cache(self, instance_id: str) -> Optional[Person]:
        cache_key = f"{self.redis_prefix_single}_{instance_id}"
        data = await self.redis.get(cache_key)
        if not data:
            return None
        return Person.model_validate(orjson.loads(data))

    async def _get_list_from_cache(
        self,
        search: str | None,
        page_size: int,
        page_number: int,
        sort: str | None = None,
    ):
        cache_key = f"{self.redis_prefix_plural}_{search or ''}_{sort or ''}_{page_size}_{page_number}"

        data = await self.redis.get(cache_key)
        if not data:
            return None

        person_list = orjson.loads(data)
        persons = [person.model_validate(person) for person in person_list]

        return persons

    async def _put_instance_to_cache(self, person: Person):
        cache_key = f"{self.redis_prefix_single}_{person.id}"
        await self.redis.set(
            cache_key,
            person.model_dump_json(),
            settings.cache_expire_time,
        )

    async def _put_list_to_cache(
        self,
        sort: str,
        page_size: int,
        page_number: int,
        persons: List[Person],
    ):
        cache_key = f"{self.redis_prefix_plural}_{sort or ''}_{page_size}_{page_number}"

        persons_json_list = [person.model_dump_json() for person in persons]
        persons_json_str = orjson.dumps(persons_json_list)

        await self.redis.set(
            cache_key,
            persons_json_str,
            settings.cache_expire_time,
        )


@lru_cache()
def get_person_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
) -> PersonService:
    return PersonService(
        redis,
        elastic,
    )
