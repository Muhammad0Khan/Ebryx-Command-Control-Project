from django.urls import path, include
from .import views
from django.contrib import admin
from .views import *


urlpatterns = [
    path('', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path("logout/", logout_view, name="logout"),
    path("admin/", admin.site.urls),
    path("api/installed_apps/", InstalledAppAPIView.as_view(), name="installed_apps"),
    path("api/cpu_data/", store_cpu_data, name="cpu_data"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("hardware_dashboard/", hardware_dashboard_view, name="hardware_dashboard"),
    path("network_dashboard/", network_dashboard_view, name="network_dashboard"),
    path("installed_apps_dashboard/", installed_apps_dashboard_view, name="installed_apps_dashboard"),
    path("token-details/<str:token>/", token_details_view, name="token_details"),
    path("api/delete_token/<str:token>/", delete_token, name="delete_token"),
    path("api/hardware_info/<str:token>/", hardware_info_page, name="hardware_info"),
    path("api/network_info/<str:token>/", network_info_page, name="network_info"),
    path("api/network_data/", store_network_data, name="network_data"),
    path("api/system_data/", store_system_data, name="system_data" ), 
    path("api/ram_data/", store_ram_data, name="ram_data"),
    path("api/disk_data/", store_disk_data, name="disk_data"),
    path("terminal/", terminal_view, name="terminal" ), 
    path("api/check_issued_commands/<str:token>/", check_issued_commands, name="check_issued_commands"),
    path("api/send_executed_commands/<str:token>/", send_executed_commands, name="send_executed_commands"),

]
