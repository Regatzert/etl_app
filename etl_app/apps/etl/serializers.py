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