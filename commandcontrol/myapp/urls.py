from django.urls import path, include
from .views import cpu_info_view, profile_view, logout_view
from authentication.views import SignUpView, CustomLoginView
from . import views

urlpatterns = [
    path("cpu_info/", cpu_info_view, name="cpu_info"),
    path("remote_cpu_info_api/", views.remote_cpu_info_api, name="remote_cpu_info_api"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/profile/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),
]