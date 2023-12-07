from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class CPUInfo(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_count = models.IntegerField()
    cpu_percent = models.FloatField()
    cpu_freq_value = models.FloatField()
    threads = models.IntegerField()
    per_cpu_percent = models.JSONField()


class RemoteCPUInfo(models.Model):
    STATUS_CHOICES = [
        ("Online", "Online"),
        ("Offline", "Offline"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    remote_ip = models.GenericIPAddressField()
    pc_name = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_count = models.IntegerField()
    cpu_percent = models.FloatField()
    cpu_freq_value = models.FloatField()
    threads = models.IntegerField()
    per_cpu_percent = models.JSONField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Online")

    def __str__(self):
        return f"Remote CPU Info for {self.user.username} ({self.remote_ip})"

class InstalledApp(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    installation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
