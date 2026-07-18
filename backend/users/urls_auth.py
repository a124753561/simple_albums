from django.urls import path
from .views_auth import login_view, refresh_view

urlpatterns = [
    path("login/", login_view, name="auth-login"),
    path("refresh/", refresh_view, name="auth-refresh"),
]
