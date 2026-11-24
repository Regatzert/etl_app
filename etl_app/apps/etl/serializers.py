from rest_framework import serializers


class ODataExtractionSerializer(serializers.Serializer):

    source_type = serializers.ChoiceField(
        choices=["odata"],
        default="odata"
    )

    url = serializers.URLField(
        required=True
    )

    username = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None
    )

    password = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None,
        write_only=True
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

    def validate_url(self, value):

        if not value.startswith(("http://", "https://")):
            raise serializers.ValidationError(
                "La URL debe utilizar HTTP o HTTPS."
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

    batch_size = serializers.IntegerField(
        required=False,
        default=1000,
        min_value=1,
        max_value=10000
    )

    def validate_dataset(self, value):

        value = value.strip()

        if not value:

            raise serializers.ValidationError(
                "El dataset no puede estar vacío."
            )

        return value

class ETLExecutionSerializer(serializers.Serializer):

    source = ODataExtractionSerializer()

    transformation = serializers.DictField(
        required=False,
        default=dict
    )

    load = serializers.DictField(
        required=True
    )

    def validate_transformation(self, value):

        mapping = value.get(
            "mapping",
            {}
        )

        types = value.get(
            "types",
            {}
        )

        include_unmapped = value.get(
            "include_unmapped",
            False
        )

        serializer = ODataTransformationSerializer(
            data={
                "records": [],
                "mapping": mapping,
                "types": types,
                "include_unmapped": include_unmapped,
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        return serializer.validated_data

    def validate_load(self, value):

        dataset = value.get("dataset")

        if not dataset:

            raise serializers.ValidationError(
                "El dataset es obligatorio."
            )

        dataset = dataset.strip()

        if not dataset:

            raise serializers.ValidationError(
                "El dataset no puede estar vacío."
            )

        batch_size = value.get(
            "batch_size",
            1000
        )

        if not isinstance(batch_size, int):

            raise serializers.ValidationError(
                "batch_size debe ser un entero."
            )

        if batch_size < 1 or batch_size > 10000:

            raise serializers.ValidationError(
                "batch_size debe estar entre 1 y 10000."
            )

        value["dataset"] = dataset

        return value

class ODataDiscoverySerializer(serializers.Serializer):
    url = serializers.URLField()
    timeout = serializers.IntegerField(
        required=False,
        default=30,
        min_value=1,
        max_value=120
    )
