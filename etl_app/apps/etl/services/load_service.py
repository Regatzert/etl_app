
from etl_app.apps.etl.load.postgresql_loader import (
    PostgreSQLLoader
)


class LoadService:

    @staticmethod
    def load_records(
        records,
        model,
        strategy,
        batch_size=1000,
        delete_filter=None,
        allow_empty=False,
        database="etl_platform",
    ):

        loader = PostgreSQLLoader(
            batch_size=batch_size,
            database=database,
        )

        return loader.load(
            records=records,
            model=model,
            strategy=strategy,
            delete_filter=delete_filter,
            allow_empty=allow_empty,
        )
