from functools import lru_cache
from typing import List, Optional

import orjson
from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.person import Person
from redis.asyncio import Redis


class PersonService:
    index = "persons"
    redis_prefix_single = "person"
    redis_prefix_plural = "persons"

    def __init__(
        self,
        redis: Redis,
        elastic: AsyncElasticsearch,
    ):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(
        self,
        person_id: str,
    ) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def filter(
        self,
        search: Optional[str],
        page_number: int,
        page_size: int,
        sort: str = None,
    ) -> list[Optional[Person]]:
        persons = await self._get_persons_from_cache(
            search=search,
            page_size=page_size,
            page_number=page_number,
            sort=sort,
        )
        if not persons:
            persons = await self._get_persons_from_elastic(
                search=search,
                page_number=page_number,
                page_size=page_size,
                sort=sort,
            )
            if not persons:
                return []
            await self._put_persons_to_cache(
                page_number=page_number,
                page_size=page_size,
                sort=sort,
                persons=persons,
            )

        return persons

    async def _get_person_from_elastic(
        self,
        person_id: str,
    ) -> Optional[Person]:
        try:
            doc = await self.elastic.get(
                index=self.index,
                id=person_id,
            )
        except NotFoundError:
            return None
        return Person(**doc["_source"])

    async def _get_persons_from_elastic(
        self,
        search: Optional[str],
        page_number: int,
        page_size: int,
        sort: str = None,
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
            asc = True
            if sort.startswith("-"):
                asc = False
            sort = [
                {
                    "{}{}".format(
                        sort if asc else sort[1:],
                        ":asc" if asc else ":desc",
                    )
                }
            ]
            query["sort"] = sort

        try:
            doc = await self.elastic.search(
                index=self.index,
                body=query,
            )
        except NotFoundError:
            return None
        persons = [Person.model_validate(doc["_source"]) for doc in doc["hits"]["hits"]]
        return persons

    async def _person_from_cache(
        self,
        person_id: str,
    ) -> Optional[Person]:
        cache_key = f"{self.redis_prefix_single}_{person_id}"
        data = await self.redis.get(cache_key)
        if not data:
            return None
        return Person.model_validate(orjson.loads(data))

    async def _get_persons_from_cache(
        self,
        search: Optional[str],
        page_size: int,
        page_number: int,
        sort: str = None,
    ):
        cache_key = f"{self.redis_prefix_plural}_{search or ''}_{sort or ''}_{page_size}_{page_number}"

        data = await self.redis.get(cache_key)
        if not data:
            return None

        person_list = orjson.loads(data)
        persons = [person.model_validate(person) for person in person_list]

        return persons

    async def _put_person_to_cache(
        self,
        person: Person,
    ):
        cache_key = f"{self.redis_prefix_single}_{person.id}"
        await self.redis.set(
            cache_key,
            person.model_dump_json(),
            settings.cache_expire_time,
        )

    async def _put_persons_to_cache(
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
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(
        redis,
        elastic,
    )
