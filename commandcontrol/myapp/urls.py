from django.urls import path
from .views import cpu_info_view
from .views import remote_cpu_info
from . import views

urlpatterns = [
    path("cpu_info/", cpu_info_view, name="cpu_info"),
    path("remote_cpu_info/", remote_cpu_info, name="remote_cpu_info"),
    path("remote_cpu_info_api/", views.remote_cpu_info_api, name="remote_cpu_info_api"),
]
