from functools import lru_cache

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.film import Film
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import RedisCacheService
from .search_service import ElasticSearchService
from .searchable_model_service import SearchableModelService


@lru_cache()
def get_film_service(
    redis: CacheStorageProtocol = Depends(get_redis), elastic: SearchEngineProtocol = Depends(get_elastic)
) -> SearchableModelService:
    cache_service = RedisCacheService(
        cache_storage=redis, prefix_plural="movies", prefix_single="movie", deserialize=Film.deserialize_cache
    )
    search_service = ElasticSearchService(search_engine=elastic, index="movies", deserialize=Film.deserialize_search)
    return SearchableModelService[Film](caching_service=cache_service, search_service=search_service)
