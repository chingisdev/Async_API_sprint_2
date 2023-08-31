from functools import lru_cache, partial

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.genre import Genre
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import GenreRedisCache
from .search_service import (
    ElasticSearchService,
    GenreElasticSearchService,
    auto_deserializer,
)
from .searchable_model_service import SearchableModelService


@lru_cache()
def get_genre_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
) -> SearchableModelService:
    redis = GenreRedisCache(cache_storage=redis, prefix_single="genre", prefix_plural="genres")
    elastic = ElasticSearchService(search_engine=elastic, index="genres", deserialize=partial(auto_deserializer, Genre))
    return SearchableModelService[Genre](caching_service=redis, search_service=elastic)
