from django.contrib import admin

# Register your models here.

from myapp.models import *

# admin.site.register(RemoteCPUInfo)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ('token', 'created_at')  # Define the fields you want to display in the admin list view

admin.site.register(APIToken, YourModelAdmin)
admin.site.register(CPUInfo)
