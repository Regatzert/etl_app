import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ODataExtractionSerializer
from .services.extraction_service import ExtractionService

from .serializers import ODataTransformationSerializer
from .services.transformation_service import TransformationService

logger = logging.getLogger(__name__)


class ODataExtractionView(APIView):

    def post(self, request):

        serializer = ODataExtractionSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        result = ExtractionService.extract_from_odata(
            url=validated_data["url"],
            username=validated_data.get("username"),
            password=validated_data.get("password"),
            timeout=validated_data["timeout"],
            max_retries=validated_data["max_retries"],
        )

        if result["status"] == "error":

            return Response(
                {
                    "status": "error",
                    "message": result["message"],
                    "source": result["source"],
                    "records_count": result["records_count"],
                    "started_at": result["started_at"],
                    "finished_at": result["finished_at"],
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(
            {
                "status": result["status"],
                "source": result["source"],
                "records_count": result["records_count"],
                "started_at": result["started_at"],
                "finished_at": result["finished_at"],
                "records": result["records"],
            },
            status=status.HTTP_200_OK
        )

class ODataTransformationView(APIView):

    def post(self, request):

        serializer = ODataTransformationSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        validated_data = serializer.validated_data

        # records = serializer.validated_data["records"]

        result = TransformationService.transform_records(
            records=validated_data["records"],
            mapping=validated_data["mapping"],
            types=validated_data["types"],
            include_unmapped=validated_data["include_unmapped"],
        )

        if result["status"] == "error":

            return Response(
                {
                    "status": "error",
                    "message": result["message"],
                    "records_count": 0,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            result,
            status=status.HTTP_200_OK
        )