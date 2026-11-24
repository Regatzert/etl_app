
from rest_framework import serializers


class ODataExtractionSerializer(serializers.Serializer):

    connection = serializers.CharField(
        required=True,
        max_length=100
    )

    source_type = serializers.ChoiceField(
        choices=["odata"],
        default="odata"
    )

    url = serializers.URLField(
        required=True
    )

    query_params = serializers.DictField(
        required=False,
        default=dict
    )

    timeout = serializers.IntegerField(
        required=False,
        default=60,
        min_value=1,
        max_value=300
    )

    max_retries = serializers.IntegerField(
        required=False,
        default=3,
        min_value=0,
        max_value=10
    )

    def validate_connection(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "La conexión es obligatoria."
            )

        return value

    def validate_url(self, value):

        if not value.startswith(("http://", "https://")):
            raise serializers.ValidationError(
                "La URL debe utilizar HTTP o HTTPS."
            )

        return value

    def validate_query_params(self, value):

        for key, parameter_value in value.items():

            if not isinstance(key, str) or not key.strip():
                raise serializers.ValidationError(
                    "Los nombres de los parámetros no pueden estar vacíos."
                )

            if parameter_value is None:
                raise serializers.ValidationError(
                    f"El parámetro '{key}' no puede tener valor None."
                )

        return value


class ODataTransformationSerializer(serializers.Serializer):

    records = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        allow_empty=True
    )

    mapping = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        default=dict
    )

    types = serializers.DictField(
        child=serializers.ChoiceField(
            choices=[
                "string",
                "integer",
                "decimal",
                "float",
                "boolean",
                "date",
                "datetime",
            ]
        ),
        required=False,
        default=dict
    )

    include_unmapped = serializers.BooleanField(
        required=False,
        default=False
    )

    def validate_mapping(self, value):

        target_fields = list(value.values())

        if len(target_fields) != len(set(target_fields)):
            raise serializers.ValidationError(
                "No se permite asignar varios campos origen "
                "al mismo campo destino."
            )

        for source_field, target_field in value.items():

            if not source_field.strip():
                raise serializers.ValidationError(
                    "Los campos origen no pueden estar vacíos."
                )

            if not target_field.strip():
                raise serializers.ValidationError(
                    "Los campos destino no pueden estar vacíos."
                )

        return value


class ETLTransformationConfigSerializer(serializers.Serializer):

    mapping = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        default=dict
    )

    types = serializers.DictField(
        child=serializers.ChoiceField(
            choices=[
                "string",
                "integer",
                "decimal",
                "float",
                "boolean",
                "date",
                "datetime",
            ]
        ),
        required=False,
        default=dict
    )

    include_unmapped = serializers.BooleanField(
        required=False,
        default=False
    )


class ODataLoadSerializer(serializers.Serializer):

    records = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        allow_empty=True
    )

    dataset = serializers.CharField(
        required=True,
        max_length=100
    )

    strategy = serializers.ChoiceField(
        choices=[
            "replace_all",
            "replace_by_filter"
        ],
        default="replace_all"
    )

    batch_size = serializers.IntegerField(
        required=False,
        default=1000,
        min_value=1,
        max_value=10000
    )

    allow_empty = serializers.BooleanField(
        required=False,
        default=False
    )

    delete_filter = serializers.DictField(
        required=False,
        allow_empty=False
    )

    def validate_dataset(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "El dataset no puede estar vacío."
            )

        return value

    def validate(self, attrs):

        strategy = attrs.get("strategy")
        delete_filter = attrs.get("delete_filter")

        if strategy == "replace_by_filter" and not delete_filter:
            raise serializers.ValidationError({
                "delete_filter": (
                    "Es obligatorio para la estrategia replace_by_filter."
                )
            })

        if strategy == "replace_all" and delete_filter:
            raise serializers.ValidationError({
                "delete_filter": (
                    "No corresponde utilizar delete_filter con replace_all."
                )
            })

        return attrs


class ETLLoadConfigSerializer(serializers.Serializer):

    dataset = serializers.CharField(
        required=True,
        max_length=100
    )

    strategy = serializers.ChoiceField(
        choices=[
            "replace_all",
            "replace_by_filter"
        ],
        default="replace_all"
    )

    batch_size = serializers.IntegerField(
        required=False,
        default=1000,
        min_value=1,
        max_value=10000
    )

    allow_empty = serializers.BooleanField(
        required=False,
        default=False
    )

    delete_filter = serializers.DictField(
        required=False,
        allow_empty=False
    )

    database = serializers.CharField(
        required=False,
        default="etl_platform",
        max_length=100
    )

    def validate_dataset(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "El dataset no puede estar vacío."
            )

        return value

    def validate_database(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "La base de datos no puede estar vacía."
            )

        return value

    def validate(self, attrs):

        strategy = attrs.get("strategy")
        delete_filter = attrs.get("delete_filter")

        if strategy == "replace_by_filter" and not delete_filter:
            raise serializers.ValidationError({
                "delete_filter": (
                    "Es obligatorio para la estrategia replace_by_filter."
                )
            })

        if strategy == "replace_all" and delete_filter:
            raise serializers.ValidationError({
                "delete_filter": (
                    "No corresponde utilizar delete_filter con replace_all."
                )
            })

        return attrs


class ETLExecutionSerializer(serializers.Serializer):

    source = ODataExtractionSerializer()

    transformation = ETLTransformationConfigSerializer(
        required=False,
        default=dict
    )

    load = ETLLoadConfigSerializer(
        required=True
    )


class ODataDiscoverySerializer(serializers.Serializer):

    connection = serializers.CharField(
        required=True,
        max_length=100
    )

    url = serializers.URLField(
        required=True
    )

    timeout = serializers.IntegerField(
        required=False,
        default=30,
        min_value=1,
        max_value=120
    )

    def validate_connection(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "La conexión es obligatoria."
            )

        return value
