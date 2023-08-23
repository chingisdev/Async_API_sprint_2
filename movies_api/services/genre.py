from functools import lru_cache
from typing import List, Optional

import orjson
from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.genre import Genre
from redis.asyncio import Redis


class GenreService:
    index = "genres"
    redis_prefix_single = "genre"
    redis_prefix_plural = "genres"

    def __init__(
        self,
        redis: Redis,
        elastic: AsyncElasticsearch,
    ):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(
        self,
        genre_id: str,
    ) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)

        return genre

    async def filter(
        self,
        search: Optional[str],
        page_number: int,
        page_size: int,
        sort: str = None,
    ) -> list[Optional[Genre]]:
        genres = await self._get_genres_from_cache(
            search=search,
            page_size=page_size,
            page_number=page_number,
            sort=sort,
        )
        if not genres:
            genres = await self._get_genres_from_elastic(
                search=search,
                page_number=page_number,
                page_size=page_size,
                sort=sort,
            )
            if not genres:
                return []
            await self._put_genres_to_cache(
                page_number=page_number,
                page_size=page_size,
                sort=sort,
                genres=genres,
            )

        return genres

    async def _get_genre_from_elastic(
        self,
        genre_id: str,
    ) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(
                index=self.index,
                id=genre_id,
            )
        except NotFoundError:
            return None
        return Genre(**doc["_source"])

    async def _get_genres_from_elastic(
        self,
        search: Optional[str],
        page_number: int,
        page_size: int,
        sort: str = None,
    ):
        query = {
            "query": {
                "multi_match": {
                    "query": search,
                    "fields": ["*"],
                }
            }
            if search
            else {"match_all": {}},
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }

        if sort:
            asc = True
            if sort.startswith("-"):
                asc = False
            sort = [
                {
                    "{}{}".format(
                        sort if asc else sort[1:],
                        ":asc" if asc else ":desc",
                    )
                }
            ]
            query["sort"] = sort

        try:
            doc = await self.elastic.search(
                index=self.index,
                body=query,
            )
        except NotFoundError:
            return None
        genres = [Genre.model_validate(doc["_source"]) for doc in doc["hits"]["hits"]]
        return genres

    async def _genre_from_cache(
        self,
        genre_id: str,
    ) -> Optional[Genre]:
        cache_key = f"{self.redis_prefix_single}_{genre_id}"
        data = await self.redis.get(cache_key)
        if not data:
            return None
        return Genre.model_validate(orjson.loads(data))

    async def _get_genres_from_cache(
        self,
        search: Optional[str],
        page_size: int,
        page_number: int,
        sort: str = None,
    ):
        cache_key = f"{self.redis_prefix_plural}_{search or ''}_{sort or ''}_{page_size}_{page_number}"

        data = await self.redis.get(cache_key)
        if not data:
            return None

        genre_list = orjson.loads(data)
        genres = [genre.model_validate(genre) for genre in genre_list]

        return genres

    async def _put_genre_to_cache(
        self,
        genre: Genre,
    ):
        cache_key = f"{self.redis_prefix_single}_{genre.id}"
        await self.redis.set(
            cache_key,
            genre.model_dump_json(),
            settings.cache_expire_time,
        )

    async def _put_genres_to_cache(
        self,
        sort: str,
        page_size: int,
        page_number: int,
        genres: List[Genre],
    ):
        cache_key = f"{self.redis_prefix_plural}_{sort or ''}_{page_size}_{page_number}"

        genres_json_list = [genre.model_dump_json() for genre in genres]
        genres_json_str = orjson.dumps(genres_json_list)

        await self.redis.set(
            cache_key,
            genres_json_str,
            settings.cache_expire_time,
        )


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(
        redis,
        elastic,
    )
