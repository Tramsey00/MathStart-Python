"""Public Content HTTP surface; R02A remains the canonical OpenAPI."""
from django.db import DatabaseError
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from config.api_http import APIError, envelope, error_response, json_response
from content.services.grade_catalogue import invalid_query, list_grades, unavailable


class GradeListView(APIView):
    authentication_classes = []  # Public catalogue is independent of identity state.
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    parser_classes = []
    metadata_class = None
    schema = None
    http_method_names = ["get"]

    def get(self, request):
        data, pagination = list_grades(request.query_params)
        body = envelope(request, data)
        body["meta"]["pagination"] = pagination
        return json_response(body)

    def handle_exception(self, error):
        if isinstance(error, APIError):
            safe = error
        elif isinstance(error, DatabaseError):
            safe = unavailable()
        elif isinstance(error, APIException):
            safe = invalid_query()
        else:
            return super().handle_exception(error)
        return error_response(self.request, safe)
