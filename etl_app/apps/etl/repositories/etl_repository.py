# apps/etl/repositories/etl_repository.py

from django.db import connection


class ETLRepository:

    @staticmethod
    def execute_procedure(
        procedure_name: str,
        parameters: tuple = ()
    ):

        allowed_procedures = {
            "sp_process_employees",
            "sp_process_products"
        }

        if procedure_name not in allowed_procedures:
            raise ValueError(
                "Procedimiento no autorizado"
            )

        placeholders = ", ".join(
            ["%s"] * len(parameters)
        )

        sql = f"""
            CALL {procedure_name}({placeholders})
        """

        with connection.cursor() as cursor:
            cursor.execute(sql, parameters)