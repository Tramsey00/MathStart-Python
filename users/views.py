from functools import wraps

from django.contrib.auth import logout as django_logout
from django.db import DatabaseError
from django.middleware.csrf import get_token
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import (
    APIException, AuthenticationFailed, MethodNotAllowed, NotAuthenticated, PermissionDenied,
)
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from . import services
from .http import APIError, envelope, error_response, json_response, parse_request


class IdentityAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]  # Private routes/services enforce R02A 401.
    renderer_classes = [JSONRenderer]
    parser_classes = []  # Strict UTF-8/duplicate-key/schema validation uses the raw body.
    metadata_class = None
    schema = None  # R02A is the sole canonical OpenAPI.

    def handle_exception(self, error):
        if isinstance(error, (NotAuthenticated, AuthenticationFailed)):
            safe = APIError(401, "AUTHENTICATION_REQUIRED", "Authentication required.")
        elif isinstance(error, PermissionDenied):
            csrf = str(error.detail).startswith("CSRF Failed")
            safe = APIError(403, "CSRF_FAILED" if csrf else "FORBIDDEN",
                            "CSRF validation failed." if csrf else "Access forbidden.")
        elif isinstance(error, (MethodNotAllowed, APIException)):
            safe = APIError(400, "INVALID_REQUEST", "Invalid request.")
        elif isinstance(error, DatabaseError):
            safe = APIError(503, "SERVICE_UNAVAILABLE", "Service temporarily unavailable.")
        else:
            return super().handle_exception(error)
        return error_response(self.request, safe)


def endpoint(methods, schema=None):
    def decorate(view):
        @wraps(view)
        @sensitive_variables("body")
        def dispatch(request):
            try:
                if request.method not in methods:
                    raise APIError(400, "INVALID_REQUEST", "Invalid request method.")
                # R02A requires the header; Django middleware checks its token/origin.
                if request.method != "GET" and not request.headers.get("X-CSRFToken"):
                    raise APIError(403, "CSRF_FAILED", "CSRF validation failed.")
                body = parse_request(request, schema) if schema else None
                return view(request, body)
            except APIError as error:
                return error_response(request, error)
            except DatabaseError:
                return error_response(request, APIError(
                    503, "SERVICE_UNAVAILABLE", "Service temporarily unavailable.",
                ))
        class Endpoint(IdentityAPIView):
            pass

        def handler(self, request, *args, **kwargs):
            return dispatch(request)

        for method in methods:
            setattr(Endpoint, method.lower(), handler)
        callback = Endpoint.as_view()
        # DRF's default anonymous CSRF exemption is unsuitable for register/login.
        # Keep Django CsrfViewMiddleware active on the actual URL callback.
        callback.csrf_exempt = False
        return sensitive_post_parameters("password")(callback)
    return decorate


@endpoint({"GET"})
def csrf(request, body):
    return json_response(envelope(request, {"csrf_token": get_token(request)}))


@endpoint({"POST"}, "RegisterRequest")
def register(request, body):
    user, response, status = services.register(request, body)
    if not request.user.is_authenticated:
        services.establish_session(request, user)
    return json_response(response, status)


@endpoint({"POST"}, "LoginRequest")
def login(request, body):
    return json_response(envelope(request, services.login(request, body)))


@endpoint({"POST"}, "EmptyRequest")
def logout(request, body):
    services.require_user(request.user)
    django_logout(request)
    return json_response(envelope(request, {"completed": True}))


@endpoint({"GET", "PATCH"})
def me(request, body):
    services.require_user(request.user)
    if request.method == "PATCH":
        body = parse_request(request, "ProfileUpdateRequest")
        data = services.update_profile(request.user, body)
    else:
        data = services.user_data(request.user)
    return json_response(envelope(request, data))


@endpoint({"POST"}, "OnboardingRequest")
def complete_onboarding(request, body):
    response, status = services.complete_onboarding(request, body)
    return json_response(response, status)
