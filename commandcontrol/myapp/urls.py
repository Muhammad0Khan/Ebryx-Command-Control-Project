from django.urls import path, include
from .import views
from django.contrib import admin
from .views import *


urlpatterns = [
    path('', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path("logout/", logout_view, name="logout"),
    path('admin/', admin.site.urls),
    path('api/installed_apps/', InstalledAppAPIView.as_view(), name='installed_apps'),
    path('api/cpu_data/', store_cpu_data, name='cpu_data'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('token-details/<str:token>/', token_details_view, name='token_details'),
    path('api/delete_token/<str:token>/', delete_token, name='delete_token'),
    path('api/cpu_info/<str:token>/', cpu_info_page, name='cpu_info'),
]