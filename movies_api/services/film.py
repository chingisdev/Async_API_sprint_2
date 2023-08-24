from functools import lru_cache
from typing import Optional

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.film import Film
from search_engine.search_engine_protocol import SearchEngineProtocol

from .cachable_service import FilmCachingService
from .elastic_service import FilmElasticService


class FilmService:
    def __init__(self, redis: CacheStorageProtocol, elastic: SearchEngineProtocol):
        self.redis = FilmCachingService(redis=redis, prefix_plural="movies", prefix_single="movie")
        self.elastic = FilmElasticService(elastic=elastic, index="movies")

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self.redis.get_instance_from_cache(film_id)
        if not film:
            film = await self.elastic.get_by_id(film_id)
            if not film:
                return None
            await self.redis.put_instance_to_cache(film)
        return film

    async def get_by_parameters(
        self, page_number: int, page_size: int, search: str | None = None, sort: str | None = None
    ) -> list[Optional[Film]]:
        films = await self.redis.get_list_from_cache(
            search=search, page_size=page_size, page_number=page_number, sort=sort
        )
        if not films:
            films = await self.elastic.get_by_parameters(
                search=search, page_number=page_number, page_size=page_size, sort=sort
            )
            if not films:
                return []
            await self.redis.put_list_to_cache(
                search=search, page_number=page_number, page_size=page_size, sort=sort, instances=films
            )
        return films


@lru_cache()
def get_film_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
) -> FilmService:
    return FilmService(
        redis,
        elastic,
    )
