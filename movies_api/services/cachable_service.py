import json
from abc import abstractmethod
from typing import Generic, List, Optional, TypeVar

import orjson
from cache_storage.cache_storage_protocol import CacheStorageProtocol
from core.config import settings
from models.film import Film
from models.genre import Genre
from models.person import Person
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class CachableService(Generic[T]):
    redis_prefix_single: str
    redis_prefix_plural: str
    redis: CacheStorageProtocol

    async def _get_instance_from_cache(self, instance_id: str) -> Optional[T]:
        cache_key = f"{self.redis_prefix_single}_{instance_id}"
        data = await self.redis.get(cache_key)
        if not data:
            return None
        return self._parse_instance_from_data(data)

    async def _get_list_from_cache(
        self,
        page_size: int,
        page_number: int,
        search: str | None = None,
        sort: str | None = None,
    ) -> List[T]:
        cache_key = f"{self.redis_prefix_plural}_{search or ''}_{sort or ''}_{page_size}_{page_number}"
        data = await self.redis.get(cache_key)
        if not data:
            return None
        items = orjson.loads(data)
        return [self._parse_instance_from_data(item) for item in items]

    async def _put_instance_to_cache(self, instance: T):
        cache_key = f"{self.redis_prefix_single}_{instance.id}"
        await self.redis.set(
            cache_key,
            instance.model_dump_json(),
            settings.cache_expire_time,
        )

    async def _put_list_to_cache(
        self,
        sort: str,
        page_size: int,
        page_number: int,
        instances: List[T],
        search: str | None = None,
    ):
        cache_key = f"{self.redis_prefix_plural}_{search or ''}_{sort or ''}_{page_size}_{page_number}"
        instances_json_list = [instance.model_dump_json() for instance in instances]
        instances_json_str = orjson.dumps(instances_json_list)
        await self.redis.set(
            cache_key,
            instances_json_str,
            settings.cache_expire_time,
        )

    @abstractmethod
    def _parse_instance_from_data(self, data: str) -> T:
        raise NotImplementedError


class FilmCachableService(CachableService[Film]):
    def _parse_instance_from_data(self, data: str) -> Film:
        data_dict = json.loads(data)
        return Film.parse_from_redis(data_dict)


class PersonCachableService(CachableService[Person]):
    def _parse_instance_from_data(self, data: str) -> Person:
        data_dict = json.loads(data)
        return Person.model_validate(data_dict)


class GenreCachableService(CachableService[Genre]):
    def _parse_instance_from_data(self, data: str) -> Genre:
        data_dict = json.loads(data)
        return Genre.model_validate(data_dict)
