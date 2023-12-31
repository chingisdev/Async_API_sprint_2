from abc import ABC, abstractmethod
from typing import Callable, Generic, List, Optional, Type, TypeVar

import orjson
from backoff.backoff import backoff_public_methods
from cache_storage.cache_storage_protocol import CacheStorageProtocol
from core.config import settings
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AbsractCacheService(ABC, Generic[T]):
    def __init__(
        self,
        cache_storage: CacheStorageProtocol,
        prefix_plural: str,
        prefix_single: str,
        deserialize: Callable[[dict | str], T],
    ):
        self.cache_storage = cache_storage
        self.key_prefix_plural = prefix_plural
        self.key_prefix_single = prefix_single
        self._deserialize = deserialize

    @abstractmethod
    async def get_instance_from_cache(self, instance_id: str) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    async def get_list_from_cache(
        self,
        page_size: int,
        page_number: int,
        search: str | None = None,
        sort: str | None = None,
    ) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    async def put_instance_to_cache(self, instance: T):
        raise NotImplementedError

    @abstractmethod
    async def put_list_to_cache(
        self,
        sort: str,
        page_size: int,
        page_number: int,
        instances: List[T],
        search: str | None = None,
    ):
        raise NotImplementedError


@backoff_public_methods()        
class RedisCacheService(AbsractCacheService):
    async def get_instance_from_cache(self, instance_id: str) -> Optional[T]:
        cache_key = f"{self.key_prefix_single}_{instance_id}"
        data = await self.cache_storage.get(cache_key)
        if not data:
            return None
        return self._deserialize(data)

    async def get_list_from_cache(
        self,
        page_size: int,
        page_number: int,
        search: str | None = None,
        sort: str | None = None,
    ) -> List[T] | None:
        cache_key = f"{self.key_prefix_plural}_{search or ''}_{sort or ''}_{page_size}_{page_number}"
        data = await self.cache_storage.get(cache_key)
        if not data:
            return None
        items = orjson.loads(data)
        return [self._deserialize(item) for item in items]

    async def put_instance_to_cache(self, instance: T):
        cache_key = f"{self.key_prefix_single}_{instance.id}"
        await self.cache_storage.set(
            cache_key,
            instance.model_dump_json(),
            settings.cache_expire_time,
        )

    async def put_list_to_cache(
        self, sort: str, page_size: int, page_number: int, instances: List[T], search: str | None = None
    ):
        cache_key = f"{self.key_prefix_plural}_{search or ''}_{sort or ''}_{page_size}_{page_number}"
        instances_json_list = [instance.model_dump_json() for instance in instances]
        instances_json_str = orjson.dumps(instances_json_list)
        await self.cache_storage.set(
            cache_key,
            instances_json_str,
            settings.cache_expire_time,
        )


def automatic_cache_deserializer(model: Type[T], data: str) -> T:
    data_dict = orjson.loads(data)
    return model.model_validate(data_dict)
