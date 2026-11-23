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