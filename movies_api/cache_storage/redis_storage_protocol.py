from typing import Any, Optional, Protocol


class RedisStorageProtocol(Protocol):
    """
    Storage implementation that uses Redis.
    """

    async def set(self, key, value, expiration_time) -> None:
        """Save state to the Redis storage."""
        ...

    async def get(self, k, default=None) -> Optional[Any]:
        """Retrieve state from the Redis storage."""
        ...

    async def close(self, close_connection_pool: Optional[bool] = None) -> None:
        """
        Closes Redis client connection

        :param close_connection_pool: decides whether to close the connection pool used
        by this Redis client, overriding Redis.auto_close_connection_pool. By default,
        let Redis.auto_close_connection_pool decide whether to close the connection
        pool.
        """
        ...
