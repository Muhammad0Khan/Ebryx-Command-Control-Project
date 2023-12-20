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
    path('signup/', signup, name='signup'),
    path('', login_view, name='login'),
    path("cpu_info/", cpu_info_view, name="home"),
    path("remote_cpu_info_api/", remote_cpu_info_api, name="remote_cpu_info_api"),
    # path("accounts/", include("django.contrib.auth.urls")),
    # path("accounts/profile/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),
    path('running_processes/', running_processes, name='running_processes'),
    path('api/generate_token/', generate_token, name='generate_token'),
    path('api/check-token/<str:token>/', check_token, name='check_token'),
     path('dashboard/', dashboard_view, name='dashboard'),
      path('token-details/<str:token>/', token_details_view, name='token_details'),
          path('api/delete_token/<str:token>/', delete_token, name='delete_token'),
          path('api/cpu_data/', store_cpu_data, name='cpu_data'),
           path('api/cpu_info/<str:token>/', cpu_info_page, name='cpu_info'),


    
]
