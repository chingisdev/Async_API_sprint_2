class BaseQueryBuilder:
    def build_query(self) -> str:
        pass


class TargetQuery(BaseQueryBuilder):
    def build_query(self) -> str:
        return """
        SELECT id
        FROM {base_table}
        WHERE updated_at >= :from_time AND updated_at < :till_time
        ORDER BY updated_at;
        """


class RelatedQuery(BaseQueryBuilder):
    def build_query(self) -> str:
        return """
        SELECT DISTINCT f.id AS film_id
        FROM {relative_table} related
        JOIN {relative_m2m_table} m2m ON related.id = m2m.{relative_id}
        JOIN {base_table} f ON m2m.{base_id} = f.id
        WHERE related.updated_at >= :from_time AND related.updated_at < :till_time;
        """


class GenreTransformQuery(BaseQueryBuilder):
    def build_query(self) -> str:
        return """
        SELECT
            g.id, g.name, g.description
            FROM content.genre g
            WHERE g.id IN :ids
        """


class MoviesTransformQuery(BaseQueryBuilder):
    def build_query(self) -> str:
        return """
        SELECT
                    fw.id,
                    fw.title,
                    fw.description,
                    fw.rating as imdb_rating,
                    COALESCE(
                        array_agg(DISTINCT p.full_name)
                        FILTER (WHERE p.id IS NOT NULL AND pfw.role = 'actor'),
                        ARRAY[]::text[]
                    ) AS actors_names,
                    COALESCE(
                        array_agg(DISTINCT p.full_name)
                        FILTER (WHERE p.id IS NOT NULL AND pfw.role = 'writer'),
                        ARRAY[]::text[]
                    ) AS writers_names,
                    COALESCE(
                        array_agg(DISTINCT p.full_name)
                        FILTER (WHERE p.id IS NOT NULL AND pfw.role = 'director'),
                        ARRAY[]::text[]
                    ) AS director,
                    COALESCE(
                        array_agg(DISTINCT g.name) FILTER (WHERE g.id IS NOT NULL),
                        ARRAY[]::text[]
                    ) AS genre,
                    COALESCE(
                        json_agg(
                            DISTINCT jsonb_build_object(
                                'id', p.id,
                                'name', p.full_name
                            )
                        ) FILTER (WHERE p.id IS NOT NULL AND pfw.role = 'actor'),
                        '[]'::json
                    ) AS actors,
                    COALESCE(
                        json_agg(
                            DISTINCT jsonb_build_object(
                                'id', p.id,
                                'name', p.full_name
                            )
                        ) FILTER (WHERE p.id IS NOT NULL AND pfw.role = 'writer'),
                        '[]'::json
                    ) AS writers
                    FROM content.film_work fw
                    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
                    LEFT JOIN content.person p ON p.id = pfw.person_id
                    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
                    LEFT JOIN content.genre g ON g.id = gfw.genre_id
                    WHERE fw.id IN :ids
                    GROUP BY fw.id, fw.title, fw.description,
                    fw.rating, fw.type, fw.created_at, fw.updated_at;
                """


class PersonTransformQuery(BaseQueryBuilder):
    def build_query(self) -> str:
        return """
        SELECT p.id,
            p.full_name,
            COALESCE(jsonb_agg(film_roles), '[]'::jsonb) AS films
        FROM content.person p
        LEFT JOIN (
            SELECT pfw.person_id,
            jsonb_build_object(
               'id', fw.id,
               'roles', COALESCE(array_agg(DISTINCT pfw.role) FILTER (WHERE pfw.role IS NOT NULL), ARRAY[]::text[])
            ) AS film_roles
            FROM content.person_film_work pfw
            LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
            GROUP BY pfw.person_id, fw.id
        ) subquery ON subquery.person_id = p.id
        WHERE p.id IN :ids
        GROUP BY p.id, p.full_name;
        """


class EarliestUpdateTimeQuery(BaseQueryBuilder):
    def build_query(self) -> str:
        return """
        SELECT MIN(updated_at)
        FROM {0}
        """
