# apps/etl/transformers/odata_transformer.py

from datetime import datetime


class ODataTransformer:

    def transform(self, records: list[dict]) -> list[dict]:

        transformed_records = []

        for record in records:

            transformed_record = self._transform_record(record)

            if transformed_record:
                transformed_records.append(transformed_record)

        return transformed_records

    def _transform_record(self, record: dict) -> dict:

        return {
            "employee_id": record.get("EmployeeID"),
            "name": self._clean_string(record.get("Name")),
            "email": self._clean_string(record.get("Email")),
            "created_at": self._parse_datetime(
                record.get("CreatedAt")
            )
        }

    @staticmethod
    def _clean_string(value):

        if value is None:
            return None

        return str(value).strip()

    @staticmethod
    def _parse_datetime(value):

        if not value:
            return None

        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )