from functools import lru_cache
from typing import Optional

from cachable_service import GenreCachableService
from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import NotFoundError
from fastapi import Depends
from models.genre import Genre
from search_engine.search_engine_protocol import SearchEngineProtocol


class GenreService(GenreCachableService):
    index = "genres"
    redis_prefix_single = "genre"
    redis_prefix_plural = "genres"

    def __init__(
        self,
        redis: CacheStorageProtocol,
        elastic: SearchEngineProtocol,
    ):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(
        self,
        genre_id: str,
    ) -> Optional[Genre]:
        genre = await self._get_instance_from_cache(genre_id)
        if not genre:
            genre = await self._get_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_instance_to_cache(genre)

        return genre

    async def get_by_parameters(
        self,
        search: Optional[str],
        page_number: int,
        page_size: int,
        sort: str = None,
    ) -> list[Optional[Genre]]:
        genres = await self._get_list_from_cache(
            search=search,
            page_size=page_size,
            page_number=page_number,
            sort=sort,
        )
        if not genres:
            genres = await self._get_list_from_elastic(
                search=search,
                page_number=page_number,
                page_size=page_size,
                sort=sort,
            )
            if not genres:
                return []
            await self._put_list_to_cache(
                page_number=page_number,
                page_size=page_size,
                sort=sort,
                instances=genres,
            )

        return genres

    async def _get_from_elastic(
        self,
        instance_id: str,
    ) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(
                index=self.index,
                id=instance_id,
            )
            return Genre(**doc["_source"])
        except NotFoundError:
            return None

    async def _get_list_from_elastic(
        self,
        search: Optional[str],
        page_number: int,
        page_size: int,
        sort: str = None,
    ):
        query = {
            "query": {"multi_match": {"query": search, "fields": ["*"], "fuzziness": "AUTO"}}
            if search
            else {"match_all": {}},
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }

        if sort:
            (sort_key, sort_order,) = (
                (sort[1:], "desc") if sort.startswith("-") else (sort, "asc")
            )
            query["sort"] = [{sort_key: sort_order}]

        try:
            doc = await self.elastic.search(
                index=self.index,
                body=query,
            )
        except NotFoundError:
            return None
        documents = doc["hits"]["hits"]
        genres = [Genre.model_validate(doc["_source"]) for doc in documents]
        return genres


@lru_cache()
def get_genre_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
) -> GenreService:
    return GenreService(
        redis,
        elastic,
    )
