from functools import lru_cache, partial

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.genre import Genre
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import RedisCache, automatic_cache_deserializer
from .search_service import ElasticSearchService, automatic_search_deserializer
from .searchable_model_service import SearchableModelService


@lru_cache()
def get_genre_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
) -> SearchableModelService:
    cache_deserializer = partial(automatic_cache_deserializer, Genre)
    search_deserializer = partial(automatic_search_deserializer, Genre)
    cache_service = RedisCache(
        cache_storage=redis,
        prefix_single="genre",
        prefix_plural="genres",
        deserialize=cache_deserializer,
    )
    search_service = ElasticSearchService(search_engine=elastic, index="genres", deserialize=search_deserializer)
    return SearchableModelService[Genre](caching_service=cache_service, search_service=search_service)
