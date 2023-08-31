from functools import lru_cache, partial

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.person import Person
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import PersonRedisCache
from .search_service import ElasticSearchService, auto_deserializer
from .searchable_model_service import SearchableModelService


@lru_cache()
def get_person_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
) -> SearchableModelService:
    redis = PersonRedisCache(cache_storage=redis, prefix_plural="persons", prefix_single="person")
    elastic = ElasticSearchService(
        search_engine=elastic, index="persons", deserialize=partial(auto_deserializer, Person)
    )
    return SearchableModelService[Person](caching_service=redis, search_service=elastic)
