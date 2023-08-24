from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from .cachable_service import CachingService
from .elastic_service import ElasticService

T = TypeVar("T", bound=BaseModel)


class SearchService(Generic[T]):
    def __init__(self, redis: CachingService, elastic: ElasticService):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[T]:
        item = await self.redis.get_instance_from_cache(film_id)
        if not item:
            item = await self.elastic.get_by_id(film_id)
            if not item:
                return None
            await self.redis.put_instance_to_cache(item)
        return item

    async def get_by_parameters(
        self, page_number: int, page_size: int, search: str | None = None, sort: str | None = None
    ) -> list[Optional[T]]:
        items = await self.redis.get_list_from_cache(
            search=search, page_size=page_size, page_number=page_number, sort=sort
        )
        if not items:
            items = await self.elastic.get_by_parameters(
                search=search, page_number=page_number, page_size=page_size, sort=sort
            )
            if not items:
                return []
            await self.redis.put_list_to_cache(
                search=search, page_number=page_number, page_size=page_size, sort=sort, instances=items
            )
        return items
