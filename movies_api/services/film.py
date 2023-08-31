from functools import lru_cache

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.film import Film
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import FilmRedisCache
from .search_service import FilmSearchService
from .searchable_model_service import SearchableModelService


@lru_cache()
def get_film_service(
    redis: CacheStorageProtocol = Depends(get_redis), elastic: SearchEngineProtocol = Depends(get_elastic)
) -> SearchableModelService:
    redis = FilmRedisCache(cache_storage=redis, prefix_plural="movies", prefix_single="movie")
    elastic = FilmSearchService(search_engine=elastic, index="movies")
    return SearchableModelService[Film](caching_service=redis, search_service=elastic)
