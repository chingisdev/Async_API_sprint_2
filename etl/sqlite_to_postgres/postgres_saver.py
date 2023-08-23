from dataclasses import astuple, fields

from psycopg2.extensions import connection as _connection


class PostgresSaver:
    def __init__(
        self,
        pg_conn: _connection,
    ):
        self.connection = pg_conn
        self.cursor = self.connection.cursor()

    def save_all_data(
        self,
        data: dict[
            str,
            list,
        ],
    ):
        for (
            table_name,
            instances,
        ) in data.items():
            if instances:
                self._clear_database(table_name)
                field_names = self._get_column_names(instances[0])
                columns = ", ".join(field_names)
                bind_values = self._prepare_data_to_insert(
                    len(field_names),
                    instances,
                )
                self.cursor.execute(
                    f"""
                    INSERT INTO content.{table_name} ({columns})
                    VALUES {bind_values}
                    ON CONFLICT (id) DO NOTHING
                    """
                )
                self.connection.commit()

    def _clear_database(
        self,
        table_name,
    ):
        self.cursor.execute(f"TRUNCATE content.{table_name} CASCADE;")

    def _prepare_data_to_insert(
        self,
        fields_length,
        instances_to_prepare,
    ):
        column_counts = ", ".join(["%s"] * fields_length)
        query_values = [
            self.cursor.mogrify(
                f"({column_counts})",
                astuple(item),
            ).decode("utf-8")
            for item in instances_to_prepare
        ]
        bind_values = ",".join(query_values)
        return bind_values

    def _get_column_names(
        self,
        data_instance,
    ):
        return [field.name for field in fields(data_instance)]
