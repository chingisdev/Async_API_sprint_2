from functools import lru_cache, partial

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from fastapi import Depends
from models.person import Person
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import RedisCacheService, automatic_cache_deserializer
from .search_service import ElasticSearchService, automatic_search_deserializer
from .searchable_model_service import SearchableModelService


@lru_cache()
def get_person_service(
    redis: CacheStorageProtocol = Depends(get_redis), elastic: SearchEngineProtocol = Depends(get_elastic)
) -> SearchableModelService:
    cache_deserializer = partial(automatic_cache_deserializer, Person)
    search_deserializer = partial(automatic_search_deserializer, Person)
    cache_service = RedisCacheService(
        cache_storage=redis,
        prefix_plural="persons",
        prefix_single="person",
        deserialize=cache_deserializer,
    )
    search_service = ElasticSearchService(search_engine=elastic, index="persons", deserialize=search_deserializer)
    return SearchableModelService[Person](caching_service=cache_service, search_service=search_service)
