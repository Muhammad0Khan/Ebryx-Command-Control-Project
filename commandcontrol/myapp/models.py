from djongo import models
from django.utils import timezone


class APIToken(models.Model):
    token = models.CharField(max_length=40, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default="offline")

    def __str__(self):
        return self.token


class CPUInfo(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    cpu_count = models.IntegerField()
    cpu_percent = models.FloatField()
    cpu_freq_value = models.FloatField()
    threads = models.IntegerField()
    percent_per_cpu = models.JSONField()

    def __str__(self):
        return f"CPU Info - ID: {self.id}, Token: {self.token}, Timestamp: {self.timestamp}"


class InstalledApp(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    installation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
