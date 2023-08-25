from typing import Any, Optional

from state.storage import BaseStorage
from time_event_decorators.backoff import backoff


class State:
    """Class for managing states."""

    def __init__(
        self,
        storage: BaseStorage,
    ) -> None:
        self.storage = storage

    @backoff()
    def set_state(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set the state for a specific key.

        :param key:
        :param value:

        :return: None
        """
        self.storage.save_state(
            {
                "key": key,
                "value": value,
            }
        )

    @backoff()
    def get_state(
        self,
        key: str,
        default: Any = None,
    ) -> Optional[Any]:
        """
        Get the state for a specific key.

        :param key:
        :param default: If nothing found by key returns value

        :return: Optional[Any]
        """

        result = self.storage.retrieve_state(key)
        if default is not None and result is None:
            return default

        return result.decode() if result else None
