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

<<<<<<< Updated upstream
=======

class SystemData(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, default=None)
    hostname = models.CharField(max_length=150, default=None)
    operating_system = models.CharField(max_length=150, default=None)
    operating_system_version = models.CharField(max_length=150, default=None)

    def __str__(self):
        return f"Token: {self.token}, Username: {self.username}"

>>>>>>> Stashed changes

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

<<<<<<< Updated upstream

class NetworkStats(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    data = models.JSONField()

    def __str__(self):
=======
class RamInfo(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.CASCADE)
    total_memory = models.FloatField()
    data = models.JSONField()

    def __str__(self):
        return f"RAM Info - Token: {self.token}"

class DiskInfo(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.CASCADE)
    total_disk = models.FloatField()
    timestamp = models.DateTimeField()
    used_disk = models.FloatField()
    free_disk = models.FloatField()
    percent_disk = models.FloatField()

    def __str__(self):
        return f"Disk Info - Token: {self.token}"
    
class RamInfo(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.CASCADE)
    total_memory = models.FloatField()
    timestamp = models.DateTimeField()
    available_memory = models.FloatField()
    used_memory = models.FloatField()
    free_memory = models.FloatField()
    percent_memory = models.FloatField()
    total_swap = models.FloatField()
    used_swap = models.FloatField()
    free_swap = models.FloatField()
    percent_swap = models.FloatField()

    def __str__(self):
        return f"RAM Info - Token: {self.token}"

class NetworkStats(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    data = models.JSONField()

    def __str__(self):
>>>>>>> Stashed changes
        return f"Network Stats - Token: {self.token}, Timestamp: {self.timestamp}"


class InstalledApp(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.CASCADE)
    data = models.JSONField()

    def __str__(self):
        return f"Installed Apps - Token: {self.token}"
<<<<<<< Updated upstream
=======

class Notifications(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=150)
    type = models.CharField(max_length=150)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification - Token: {self.token}, Timestamp: {self.timestamp}"
    
class Command(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.CASCADE)
    command = models.CharField(max_length=150)
    executed = models.BooleanField(default=False)
    response = models.JSONField(default=None)

    def __str__(self):
        return f"Command - Token: {self.token}, Command: {self.command}"
>>>>>>> Stashed changes
