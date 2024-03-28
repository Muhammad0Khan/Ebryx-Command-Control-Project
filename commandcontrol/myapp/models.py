from djongo import models
from django.utils import timezone


class APIToken(models.Model):
    token = models.CharField(max_length=40, primary_key=True)
    username = models.CharField(max_length=150, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default="offline")

    def __str__(self):
        return f"Token: {self.token}, Username: {self.username}"


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


class NetworkStats(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    data = models.JSONField()

    def __str__(self):
        return f"Network Stats - Token: {self.token}, Timestamp: {self.timestamp}"


class InstalledApp(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.CASCADE)
    data = models.JSONField()

    def __str__(self):
        return f"Installed Apps - Token: {self.token}"
