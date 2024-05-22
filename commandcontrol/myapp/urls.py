from django.urls import path, include
from . import views
from django.contrib import admin
from .views import *


urlpatterns = [
    path("", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("logout/", logout_view, name="logout"),
    path("admin/", admin.site.urls),
<<<<<<< Updated upstream
    path("api/set_status_offline/", set_status_offline, name="set_status_offline"),
    path("api/set_status_online/", update_token_status, name="set_status_online"),
    path("api/check_token/<str:token>/", check_token, name="check_token"),
    path("api/installed_apps/", store_installed_apps, name="installed_apps"),
    path("api/check_username/<str:username>/", check_username, name="check_username"),
    path("api/cpu_data/", store_cpu_data, name="cpu_data"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("token-details/<str:token>/", token_details_view, name="token_details"),
=======
    path("api/installed_apps/", store_installed_apps, name="installed_apps"),
    path("api/cpu_data/", store_cpu_data, name="cpu_data"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("cpu_dashboard/", cpu_dashboard_view, name="cpu_dashboard"),
    path("network_dashboard/", network_dashboard_view, name="network_dashboard"),
    path("hardware_dashboard/", hardware_dashboard_view, name="hardware_dashboard"),
    path(
        "installed_apps_dashboard/",
        installed_apps_dashboard_view,
        name="installed_apps_dashboard",
    ),
    path("api/token_details/<str:token>/", token_details_view, name="token_details"),
>>>>>>> Stashed changes
    path("api/delete_token/<str:token>/", delete_token, name="delete_token"),
    path("api/cpu_info/<str:token>/", cpu_info_page, name="cpu_info"),
    path("api/hardware_info/<str:token>/", hardware_info_page, name="hardware_info"),
    path("api/network_info/<str:token>/", network_info_page, name="network_info"),
    path("api/network_data/", store_network_data, name="network_data"),
<<<<<<< Updated upstream
=======
    path("api/system_data/", store_system_data, name="system_data"),
    path("api/ram_data/", store_ram_data, name="ram_data"),
    path("api/disk_data/", store_disk_data, name="disk_data"),
    path("terminal/", terminal_view, name="terminal"),
    path(
        "api/generate_terminal/<str:token>/",
        generate_terminal,
        name="generate_terminal",
    ),
    path("api/generate_report/<str:token>/", generate_reports, name="generate_report"),
    path(
        "api/check_issued_commands/<str:token>/",
        check_issued_commands,
        name="check_issued_commands",
    ),
    path(
        "api/send_executed_commands/<str:token>/",
        send_executed_commands,
        name="send_executed_commands",
    ),
>>>>>>> Stashed changes
]
