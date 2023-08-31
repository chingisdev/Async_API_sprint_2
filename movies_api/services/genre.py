from functools import lru_cache

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.genre import Genre
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import GenreRedisCache
from .search_service import GenreSearchService
from .searchable_model_service import SearchableModelService


@lru_cache()
def get_genre_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
) -> SearchableModelService:
    redis = GenreRedisCache(cache_storage=redis, prefix_single="genre", prefix_plural="genres")
    elastic = GenreSearchService(search_engine=elastic, index="genres")
    return SearchableModelService[Genre](caching_service=redis, search_service=elastic)
