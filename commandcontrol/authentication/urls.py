from django.urls import path
from .views import admin_signup, admin_login, view_recent_details, admin_view

urlpatterns = [
    path("admin/signup/", admin_signup, name="admin_signup"),
    path("admin/login/", admin_login, name="admin_login"),
    path(
        "admin/view_recent_details/<str:pc_name>/",
        view_recent_details,
        name="view_recent_details",
    ),
    path("admin/view/", admin_view, name="admin_view"),
]
