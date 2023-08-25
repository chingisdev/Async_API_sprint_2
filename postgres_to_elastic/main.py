from extract_transform.boundaries import get_query_boundaries
from extract_transform.extract_settings import setup_database_orchester
from extract_transform.postgres_orchester import PostgresOrchester
from extract_transform.query_manager import PostgresTableName
from load.elastic_config import ELASTIC_CONFIGS, ElasticIndexName
from load.elastic_search_loader import ElasticLoader
from project_setup.env_settings import Settings
from redis.client import Redis
from state.state import State
from state.storage import RedisStorage
from time_event_decorators.repeat_after_sleep import repeat_after_sleep

ELASTIC_INDEXES = list(ElasticIndexName)
TABLE_NAMES = list(PostgresTableName)


@repeat_after_sleep
def synchronise_postgres_elastic(
    loader: ElasticLoader,
    extractor: PostgresOrchester,
    state,
):
    time_boundaries = None
    for index in ELASTIC_INDEXES:
        current_state_key = f"{index.value}_update"
        update_state = state.get_state(current_state_key)
        if update_state is None:
            update_state = extractor.extract_min_update_time()
        time_boundaries = get_query_boundaries(last_update_time=update_state)
        data_to_load = extractor.extract_transformed_data(
            index=index,
            table_names=TABLE_NAMES,
            boundaries=time_boundaries,
        )
        loader.load_data_to_es(
            es_data=data_to_load,
            es_index=index,
        )
        state.set_state(
            current_state_key,
            time_boundaries.till_time.isoformat(),
        )
    return time_boundaries.till_time


if __name__ == "__main__":
    settings = Settings()
    elastic_search_loader = ElasticLoader(
        es_url=settings.elastic_url,
        es_indexes=ELASTIC_INDEXES,
        es_configs=ELASTIC_CONFIGS,
    )
    redis_storage = RedisStorage(redis_adapter=Redis.from_url(url=settings.redis_url))
    state = State(storage=redis_storage)
    postgres_receiver_orchester = setup_database_orchester(settings.database_url)
    while True:
        synchronise_postgres_elastic(
            loader=elastic_search_loader,
            extractor=postgres_receiver_orchester,
            state=state,
        )
