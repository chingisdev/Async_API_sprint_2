from cache_storage.cache_storage_protocol import CacheStorageProtocol

redis: CacheStorageProtocol | None = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> CacheStorageProtocol:
    return redis
