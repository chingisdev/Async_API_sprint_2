from functools import lru_cache
from typing import List, Optional

import orjson
from cache_storage.cache_storage_protocol import CacheStorageProtocol
from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import NotFoundError
from fastapi import Depends
from models.film import Film
from search_engine.search_engine_protocol import SearchEngineProtocol


class FilmService:
    redis_prefix_single = "movie"
    redis_prefix_plural = "movies"
    index = "movies"

    def __init__(
        self,
        redis: CacheStorageProtocol,
        elastic: SearchEngineProtocol,
    ):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._get_from_cache(film_id)
        if not film:
            film = await self._get_from_elastic(film_id)
            if not film:
                return None
            await self._put_instance_to_cache(film)

        return film

    async def get_by_parameters(
        self,
        page_number: int,
        page_size: int,
        search: str | None = None,
        sort: str | None = None,
    ) -> list[Optional[Film]]:
        films = await self._get_list_from_cache(
            search=search,
            page_size=page_size,
            page_number=page_number,
            sort=sort,
        )
        if not films:
            films = await self._get_list_from_elastic(
                search=search,
                page_number=page_number,
                page_size=page_size,
                sort=sort,
            )
            if not films:
                return []
            await self._put_list_to_cache(
                search=search,
                page_number=page_number,
                page_size=page_size,
                sort=sort,
                films=films,
            )

        return films

    async def _get_from_elastic(
        self,
        instance_id: str,
    ) -> Optional[Film]:
        try:
            doc = await self.elastic.get(
                index=self.index,
                id=instance_id,
            )
            return Film.parse_from_elastic(doc)
        except NotFoundError:
            return None

    async def _get_list_from_elastic(
        self,
        page_number: int,
        page_size: int,
        search: str | None = None,
        sort: str | None = None,
    ):
        query = {
            "query": {
                "multi_match": {
                    "query": search,
                    "fields": ["*"],
                    "fuzziness": "AUTO",
                }
            }
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
        films = [Film.parse_from_elastic(doc) for doc in documents]
        return films

    async def _get_from_cache(self, instance_id: str) -> Optional[Film]:
        cache_key = f"{self.redis_prefix_single}_{instance_id}"
        data = await self.redis.get(cache_key)
        if not data:
            return None
        film = Film.parse_from_redis(data)
        return film

    async def _get_list_from_cache(
        self,
        search: str | None,
        page_size: int,
        page_number: int,
        sort: str | None = None,
    ):
        cache_key = f"{self.redis_prefix_plural}_{search or ''}_{sort or ''}_{page_size}_{page_number}"

        data = await self.redis.get(cache_key)
        if not data:
            return None

        film_list = orjson.loads(data)
        films = [Film.parse_from_redis(film) for film in film_list]

        return films

    async def _put_instance_to_cache(self, film: Film):
        cache_key = f"{self.redis_prefix_single}_{film.id}"
        await self.redis.set(
            cache_key,
            film.model_dump_json(),
            settings.cache_expire_time,
        )

    async def _put_list_to_cache(
        self,
        sort: str,
        page_size: int,
        page_number: int,
        films: List[Film],
        search: str,
    ):
        cache_key = f"{self.redis_prefix_plural}_{search or ''}_{sort or ''}_{page_size}_{page_number}"

        films_json_list = [film.model_dump_json() for film in films]
        films_json_str = orjson.dumps(films_json_list)

        await self.redis.set(
            cache_key,
            films_json_str,
            settings.cache_expire_time,
        )


@lru_cache()
def get_film_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
) -> FilmService:
    return FilmService(
        redis,
        elastic,
    )
