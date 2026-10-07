from django.urls import path

from .ui_views import account

app_name = "users_ui"
urlpatterns = [path("", account, name="account")]
