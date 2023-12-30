from django.db import models
from django.utils import timezone



class CPUInfo(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_count = models.IntegerField()
    cpu_percent = models.FloatField()
    cpu_freq_value = models.FloatField()
    threads = models.IntegerField()
    per_cpu_percent = models.JSONField()



class InstalledApp(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    installation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class APIToken(models.Model):
    token = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class InstalledApp(models.Model):
    token = models.CharField(max_length=50)
    data = models.JSONField()

    def __str__(self):
        return f"InstalledApp - Token: {self.token}"
    