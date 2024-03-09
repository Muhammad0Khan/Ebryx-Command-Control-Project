from django.contrib import admin

# Register your models here.

from myapp.models import *


# admin.site.register(RemoteCPUInfo)
class YourModelAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "created_at",
        "last_active",
        "status",
    )  # Define the fields you want to display in the admin list view


class CPUInfoAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "timestamp",
        "cpu_count",
        "cpu_percent",
        "cpu_freq_value",
        "threads",
        "percent_per_cpu",
    )  # Define the fields you want to display in the admin list view


class NetworkInfoAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "data",
    )


class InstalledAppAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "data",
    )


admin.site.register(APIToken, YourModelAdmin)
admin.site.register(CPUInfo, CPUInfoAdmin)
admin.site.register(NetworkStats, NetworkInfoAdmin)
admin.site.register(InstalledApp, InstalledAppAdmin)
