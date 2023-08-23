from api.v1 import films, genres, persons
from core.config import settings
from db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

app = FastAPI(
    title=f"Read-only API for {settings.project_name}",
    description="Information about films, genres and people involved in the creation of works",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    elastic.es = AsyncElasticsearch(hosts=[settings.elastic_url])


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


# Подключаем роутер к серверу, указав префикс /v1/films
app.include_router(
    films.router,
    prefix="/api/v1/films",
)
app.include_router(
    genres.router,
    prefix="/api/v1/genres",
)
app.include_router(
    persons.router,
    prefix="/api/v1/persons",
)
