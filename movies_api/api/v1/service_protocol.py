from typing import List, Optional, Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ModelServiceProtocol(Protocol[T]):
    async def get_by_id(self, model_id: str) -> Optional[T]:
        ...

    async def get_many_by_parameters(
        self, search: Optional[str], page_number: int, page_size: int, sort: str = None
    ) -> List[Optional[T]]:
        ...
