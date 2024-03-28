from django.urls import path, include
from . import views
from django.contrib import admin
from .views import *


urlpatterns = [
    path("", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("logout/", logout_view, name="logout"),
    path("admin/", admin.site.urls),
    path("api/generate_token/", generate_token, name="generate_token"),
    path("api/set_status_offline/", set_status_offline, name="set_status_offline"),
    path("api/check_token/<str:token>/", check_token, name="check_token"),
    path("api/installed_apps/", store_installed_apps, name="installed_apps"),
    path("api/check_username/<str:username>/", check_username, name="check_username"),
    path("api/cpu_data/", store_cpu_data, name="cpu_data"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("token-details/<str:token>/", token_details_view, name="token_details"),
    path("api/delete_token/<str:token>/", delete_token, name="delete_token"),
    path("api/cpu_info/<str:token>/", cpu_info_page, name="cpu_info"),
    path("api/network_info/<str:token>/", network_info_page, name="network_info"),
    path("api/network_data/", store_network_data, name="network_data"),
]
