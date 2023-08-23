from cache_storage.redis_storage_protocol import RedisStorageProtocol

redis: RedisStorageProtocol | None = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> RedisStorageProtocol:
    return redis
