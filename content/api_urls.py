from django.urls import path

from .api_views import GradeListView

app_name = "content_api"
urlpatterns = [path("grades/", GradeListView.as_view(), name="grades")]
