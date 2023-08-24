from functools import lru_cache
from typing import Optional

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.person import Person
from search_engine.search_engine_protocol import SearchEngineProtocol

from .cachable_service import PersonCachableService
from .elastic_service import PersonElasticService


class PersonService(PersonCachableService):
    redis_prefix_single = "person"
    redis_prefix_plural = "persons"

    def __init__(
        self,
        redis: CacheStorageProtocol,
        elastic: SearchEngineProtocol,
    ):
        self.redis = redis
        self.elastic = PersonElasticService(elastic=elastic, index="persons")

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._get_instance_from_cache(person_id)
        if not person:
            person = await self.elastic.get_by_id(person_id)
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
            persons = await self.elastic.get_by_parameters(
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
                instances=persons,
            )

        return persons


@lru_cache()
def get_person_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
) -> PersonService:
    return PersonService(
        redis,
        elastic,
    )
