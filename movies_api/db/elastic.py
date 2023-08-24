from search_engine.search_engine_protocol import SearchEngineProtocol

es: SearchEngineProtocol | None = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> SearchEngineProtocol:
    return es
