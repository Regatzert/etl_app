from django.apps import AppConfig


class ETLConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"

    name = "etl_app.apps.etl"

    verbose_name = "Procesos ETL"