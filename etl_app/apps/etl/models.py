from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

class ETLDataRecord(models.Model):

    dataset = models.CharField(
        max_length=100,
        db_index=True
    )

    data = models.JSONField(encoder=DjangoJSONEncoder)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        db_table = "etl_data_records"

        ordering = ["id"]

        indexes = [
            models.Index(
                fields=["dataset", "created_at"],
                name="etl_dataset_created_idx"
            )
        ]

    def __str__(self):

        return f"{self.dataset} - {self.id}"