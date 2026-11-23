# apps/etl/orchestrators/etl_orchestrator.py

from apps.etl.extractors.odata_extractor import ODataExtractor
from apps.etl.transformers.odata_transformer import ODataTransformer
from apps.etl.loaders.postgres_loader import PostgresLoader


class ETLOrchestrator:

    def __init__(self):

        self.extractor = ODataExtractor()
        self.transformer = ODataTransformer()
        self.loader = PostgresLoader()

    def execute(self, url: str, requested_by: str):

        execution = self._create_execution(
            url=url,
            requested_by=requested_by
        )

        try:

            raw_data = self.extractor.extract(url)

            transformed_data = self.transformer.transform(
                raw_data
            )

            loaded_records = self.loader.load(
                transformed_data
            )

            self._complete_execution(
                execution=execution,
                extracted=len(raw_data),
                transformed=len(transformed_data),
                loaded=loaded_records
            )

            return {
                "execution_id": execution.id,
                "status": "COMPLETED",
                "records_extracted": len(raw_data),
                "records_transformed": len(transformed_data),
                "records_loaded": loaded_records
            }

        except Exception as exception:

            self._fail_execution(
                execution=execution,
                error=str(exception)
            )

            raise