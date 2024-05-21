"""
URL configuration for commandcontrol project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from myapp.views import *


urlpatterns = [
    path("admin/", admin.site.urls),
    path("myapp/", include("myapp.urls")),
    path('signup/', signup_view, name='signup'),
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path("logout/", logout_view, name="logout"),
    path("api/generate_token/", generate_token, name="generate_token"),
    path("api/check-token/<str:token>/", check_token, name="check_token"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("hardware_dashboard/", hardware_dashboard_view, name="hardware_dashboard"),
    path("network_dashboard/", network_dashboard_view, name="network_dashboard"),
    path(
        "installed_apps_dashboard/",
        installed_apps_dashboard_view,
        name="installed_apps_dashboard",
    ),
    path("token-details/<str:token>/", token_details_view, name="token_details"),
    path("api/delete_token/<str:token>/", delete_token, name="delete_token"),
    path("api/cpu_data/", store_cpu_data, name="cpu_data"),
    path("api/hardware_info/<str:token>/", hardware_info_page, name="hardware_info"),
    path("api/network_info/<str:token>/", network_info_page, name="network_info"),
    path("api/network_data/", store_network_data, name="network_data"),
    path("index/", index_view, name="index"),
    path("blank", blank_view, name="blank"),
    path("api/system_data/", store_system_data, name="system_data" ), 
    path("report/", reports_view, name="report" ), 
    path("api/generate_report/<str:token>/", generate_reports, name="generate_report" ), 
    path("terminal/", terminal_view, name="terminal" ), 
    path("api/generate_terminal/<str:token>/", generate_terminal, name="generate_terminal" ), 
    path("api/check-commands/<str:token>/", check_issued_commands, name="check-commands" ), 
    path("api/ram_data/", store_ram_data, name="ram_data"),
    path("api/disk_data/", store_disk_data, name="disk_data"),
    path("api/check_issued_commands/<str:token>/", check_issued_commands, name="check_issued_commands"),
    path("api/send_executed_commands/<str:token>/", send_executed_commands, name="send_executed_commands"),
    path("api/generate_pdf_report/<str:token>/", generate_pdf_report, name="generate_pdf_report"),

]
