from functools import lru_cache

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.genre import Genre
from search_engine.search_engine_protocol import SearchEngineProtocol

from .cachable_service import GenreCachingService
from .elastic_service import GenreElasticService
from .search_service import SearchService


@lru_cache()
def get_genre_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
) -> SearchService:
    redis = GenreCachingService(redis=redis, prefix_single="genre", prefix_plural="genres")
    elastic = GenreElasticService(elastic=elastic, index="genres")
    return SearchService[Genre](redis=redis, elastic=elastic)
