from etl_app.apps.data.repositories.data_repository import (
    DataRepository
)


class DataService:

    QUERIES = {

        "northwind_products": {
            "function": "fn_get_northwind_products",
            "count_function": "fn_count_northwind_products",
            "description": "Consulta productos Northwind",
        },
        "northwind_categories": {
            "function": "fn_get_northwind_categories",
            "count_function": "fn_count_northwind_categories",
            "description": "Consulta categorías Northwind",
        },
        "northwind_suppliers": {
            "function": "fn_get_northwind_suppliers",
            "count_function": "fn_count_northwind_suppliers",
            "description": "Consulta proveedores Northwind",
        },

    }

    @classmethod
    def get_data(
        cls,
        dataset: str,
        page: int = 1,
        page_size: int = 50
    ) -> dict:

        query_config = cls.QUERIES.get(dataset)

        if not query_config:

            raise ValueError(
                f"Dataset no soportado: {dataset}"
            )

        offset = (page - 1) * page_size

        records = DataRepository.execute_function(
            function_name=query_config["function"],
            params=[page_size, offset]
        )

        total_records = DataRepository.execute_scalar(
            function_name=query_config["count_function"]
        )

        return {
            "dataset": dataset,
            "count": total_records,
            "page": page,
            "page_size": page_size,
            "total_pages": (
                (total_records + page_size - 1) // page_size
                if total_records
                else 0
            ),
            "results": records,
        }