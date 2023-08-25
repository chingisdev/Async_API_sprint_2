from functools import lru_cache
from typing import Optional

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.person import Person
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import PersonCachingService
from .elastic_service import PersonSearchService
from .search_service import SearchableModelService


@lru_cache()
def get_person_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
) -> SearchableModelService:
    redis = PersonCachingService(cache_storage=redis, prefix_plural="persons", prefix_single="person")
    elastic = PersonSearchService(search_engine=elastic, index="persons")
    return SearchableModelService[Person](redis=redis, elastic=elastic)
