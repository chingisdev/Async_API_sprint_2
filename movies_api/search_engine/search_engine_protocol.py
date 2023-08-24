from typing import Protocol


class SearchEngineProtocol(Protocol):
    async def get(self, index, id):
        ...

    async def search(self, index, body):
        ...

    async def close(self):
        ...
