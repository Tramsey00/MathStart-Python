from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path("auth/csrf/", views.csrf, name="csrf"),
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login, name="login"),
    path("auth/logout/", views.logout, name="logout"),
    path("users/me/", views.me, name="me"),
    path("onboarding/complete/", views.complete_onboarding, name="complete_onboarding"),
]
