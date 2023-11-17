from django.db import models
from django.utils import timezone


class CPUInfo(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_count = models.IntegerField()
    cpu_percent = models.FloatField()
    cpu_freq_value = models.FloatField()
    threads = models.IntegerField()
    per_cpu_percent = models.JSONField()


class RemoteCPUInfo(models.Model):
    remote_ip = models.GenericIPAddressField(primary_key=True)
    cpu_count = models.IntegerField()
    cpu_percent = models.FloatField()
    cpu_freq_value = models.FloatField()
    threads = models.IntegerField()
    per_cpu_percent = models.JSONField()

    def __str__(self):
        return f"Remote CPU Info for {self.remote_ip}"
