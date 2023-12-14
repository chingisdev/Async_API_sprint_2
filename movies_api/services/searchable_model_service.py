from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

from .caching_service import AbsractCacheService
from .search_service import AbstractSearchService

T = TypeVar("T", bound=BaseModel)


class SearchableModelService(Generic[T]):
    def __init__(self, caching_service: AbsractCacheService, search_service: AbstractSearchService):
        self.cache = caching_service
        self.search = search_service

    async def get_by_id(self, film_id: str) -> Optional[T]:
        item = await self.cache.get_instance_from_cache(film_id)
        if not item:
            item = await self.search.get_by_id(film_id)
            if not item:
                return None
            await self.cache.put_instance_to_cache(item)
        return item

    async def get_many_by_parameters(
        self, page_number: int, page_size: int, search: str | None = None, sort: str | None = None
    ) -> List[Optional[T]]:
        items = await self.cache.get_list_from_cache(
            search=search, page_size=page_size, page_number=page_number, sort=sort
        )
        if not items:
            items = await self.search.get_by_parameters(
                search=search, page_number=page_number, page_size=page_size, sort=sort
            )
            if not items:
                return []
            await self.cache.put_list_to_cache(
                search=search, page_number=page_number, page_size=page_size, sort=sort, instances=items
            )
        return items

    async def get_many_by_ids(self, ids: List[str]) -> List[Optional[T]]:
        items = [await self.cache.get_instance_from_cache(entity_id) for entity_id in ids]
        missing_ids = [entity_id for entity_id, item in zip(ids, items) if item is None]

        if missing_ids:
            for missing_id in missing_ids:
                item = await self.search.get_by_id(missing_id)
                if item:
                    await self.cache.put_instance_to_cache(item)
                    items[ids.index(missing_id)] = item

        return items
