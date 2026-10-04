"""MS7-I03 presentation only; identity mutations stay in the existing API."""
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def account(request):
    response = render(request, "users/account.html")
    response["Cache-Control"] = "private, no-store"
    return response
