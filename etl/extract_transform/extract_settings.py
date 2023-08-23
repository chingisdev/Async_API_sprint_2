from extract_transform.postgres_extractor import PostgresReceiver
from extract_transform.postgres_orchester import PostgresOrchester
from extract_transform.query_builder import (
    EarliestUpdateTimeQuery,
    GenreTransformQuery,
    MoviesTransformQuery,
    PersonTransformQuery,
    RelatedQuery,
    TargetQuery,
)
from extract_transform.query_manager import (
    IntermediateTable,
    PostgresTableName,
    QueryManager,
    TableQuery,
)
from extract_transform.schemas import FilmWork, Genre, Person
from load.elastic_config import ElasticIndexName


def get_movie_receiver(
    database_url,
) -> PostgresReceiver:
    movie_query_manager = QueryManager(
        base_table=PostgresTableName.FILM_WORK,
        queries={
            TableQuery.TARGET.value: TargetQuery(),
            TableQuery.RELATED.value: RelatedQuery(),
            TableQuery.TRANSFORM.value: MoviesTransformQuery(),
            TableQuery.GET_EARLIEST_UPDATE_TIME.value: EarliestUpdateTimeQuery(),
        },
        relative_tables={
            PostgresTableName.GENRE.value: IntermediateTable(
                table_name="content.genre_film_work",
                main_id_field="film_work_id",
                related_id_field="genre_id",
            ),
            PostgresTableName.PERSON.value: IntermediateTable(
                table_name="content.person_film_work",
                main_id_field="film_work_id",
                related_id_field="person_id",
            ),
        },
    )

    return PostgresReceiver(
        index=ElasticIndexName.MOVIE,
        query_manager=movie_query_manager,
        schema=FilmWork,
        database_url=database_url,
    )


def get_genre_receiver(
    database_url,
) -> PostgresReceiver:
    genre_query_manager = QueryManager(
        base_table=PostgresTableName.GENRE,
        queries={
            TableQuery.TARGET.value: TargetQuery(),
            TableQuery.RELATED.value: RelatedQuery(),
            TableQuery.TRANSFORM.value: GenreTransformQuery(),
            TableQuery.GET_EARLIEST_UPDATE_TIME.value: EarliestUpdateTimeQuery(),
        },
        relative_tables=None,
    )

    return PostgresReceiver(
        index=ElasticIndexName.GENRE,
        query_manager=genre_query_manager,
        schema=Genre,
        database_url=database_url,
    )


def get_person_receiver(
    database_url,
) -> PostgresReceiver:
    person_query_manager = QueryManager(
        base_table=PostgresTableName.PERSON,
        queries={
            TableQuery.TARGET.value: TargetQuery(),
            TableQuery.RELATED.value: RelatedQuery(),
            TableQuery.TRANSFORM.value: PersonTransformQuery(),
            TableQuery.GET_EARLIEST_UPDATE_TIME.value: EarliestUpdateTimeQuery(),
        },
        relative_tables={
            PostgresTableName.FILM_WORK.value: IntermediateTable(
                table_name="content.person_film_work",
                main_id_field="person_id",
                related_id_field="film_work_id",
            ),
        },
    )

    return PostgresReceiver(
        index=ElasticIndexName.PERSON,
        query_manager=person_query_manager,
        schema=Person,
        database_url=database_url,
    )


def setup_database_orchester(
    database_url,
) -> PostgresOrchester:
    movie_receiver = get_movie_receiver(database_url)
    genre_receiver = get_genre_receiver(database_url)
    person_receiver = get_person_receiver(database_url)

    return PostgresOrchester(
        extractors=[
            person_receiver,
            genre_receiver,
            movie_receiver,
        ]
    )
