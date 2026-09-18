from django.http import (
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)

from .models import Redirect


class RedirectFallbackMiddleware:
    """
    Проверяет таблицу Redirect, только если обычный маршрут
    Django вернул ошибку 404.

    Благодаря этому редиректы не мешают действующим страницам.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code != 404:
            return response

        request_path = request.path

        redirect_rule = (
            Redirect.objects.filter(
                old_path=request_path,
                is_active=True,
            )
            .only(
                "new_path",
                "is_permanent",
            )
            .first()
        )

        if redirect_rule is None:
            return response

        # Защита от бесконечного редиректа.
        if redirect_rule.new_path == request_path:
            return response

        if redirect_rule.is_permanent:
            return HttpResponsePermanentRedirect(
                redirect_rule.new_path
            )

        return HttpResponseRedirect(
            redirect_rule.new_path
        )