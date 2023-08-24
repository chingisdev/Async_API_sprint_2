from functools import lru_cache
from typing import Optional

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.film import Film
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import FilmCachingService
from .elastic_service import FilmElasticService
from .search_service import SearchService


@lru_cache()
def get_film_service(
    redis: CacheStorageProtocol = Depends(get_redis), elastic: SearchEngineProtocol = Depends(get_elastic)
) -> SearchService:
    redis = FilmCachingService(redis=redis, prefix_plural="movies", prefix_single="movie")
    elastic = FilmElasticService(elastic=elastic, index="movies")
    return SearchService[Film](redis=redis, elastic=elastic)
