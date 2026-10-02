from django.conf import settings
from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("", views.home, name="home"),
    path("<slug:slug>/", views.page_detail, name="page_detail"),
]

if settings.DEBUG:
    urlpatterns.insert(0, path("__ui__/foundation/", views.ui_foundation, name="ui_foundation"))
