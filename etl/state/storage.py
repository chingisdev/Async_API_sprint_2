from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from redis.client import Redis


class BaseStorage(ABC):
    """Abstract state storage.

    Allows saving and retrieving state information.
    The actual storage implementation can vary, for example, it could
    use a database or a distributed file storage.
    """

    @abstractmethod
    def save_state(
        self,
        state: Dict[str, Any],
    ) -> None:
        """Save state to the storage."""

    @abstractmethod
    def retrieve_state(
        self,
        key: str,
    ) -> Optional[Any]:
        """Retrieve state from the storage."""


class RedisStorage(BaseStorage):
    """
    Storage implementation that uses Redis.
    """

    def __init__(
        self,
        redis_adapter: Redis,
    ) -> None:
        self.redis_adapter = redis_adapter

    def save_state(
        self,
        state: Dict[str, Any],
    ) -> None:
        """Save state to the Redis storage."""

        self.redis_adapter.set(
            state["key"],
            state["value"],
        )

    def retrieve_state(
        self,
        key: str,
    ) -> Optional[Any]:
        """Retrieve state from the Redis storage."""

        return self.redis_adapter.get(key)
