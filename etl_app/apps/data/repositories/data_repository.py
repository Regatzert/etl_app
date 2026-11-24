from django.db import connection


class DataRepository:

    @staticmethod
    def execute_function(
        function_name: str,
        params: list | None = None
    ) -> list[dict]:

        params = params or []

        with connection.cursor() as cursor:

            placeholders = ", ".join(
                ["%s"] * len(params)
            )

            query = (
                f"SELECT * FROM {function_name}"
                f"({placeholders})"
            )

            cursor.execute(query, params)

            columns = [
                column[0]
                for column in cursor.description
            ]

            rows = cursor.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    @staticmethod
    def execute_scalar(
        function_name: str,
        params: list | None = None
    ):

        params = params or []

        with connection.cursor() as cursor:

            placeholders = ", ".join(
                ["%s"] * len(params)
            )

            query = (
                f"SELECT {function_name}"
                f"({placeholders})"
            )

            cursor.execute(query, params)

            result = cursor.fetchone()

            return result[0] if result else None