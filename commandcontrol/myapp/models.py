from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .firebase_init import initialize_firebase

from firebase_admin import db


firebase_app = initialize_firebase()



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

class APIToken(models.Model):
    token = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class InstalledApp(models.Model):
    token = models.CharField(max_length=50)
    data = models.JSONField()

    def __str__(self):
        return f"InstalledApp - Token: {self.token}"
    


class FirebaseUser(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # You should hash passwords before storing them

    def save_to_firebase(self):
        user_data = {
            'email': self.email,
            'password': self.password,
        }
        # Assuming 'users' is the root node for users in your Firebase RTDB
        users_ref = db.reference('users', app=firebase_app)
        users_ref.child(self.email.replace('.', ',')).set(user_data)

    @classmethod
    def fetch_from_firebase(cls, email):
        users_ref = db.reference('users', app=firebase_app)
        user_data = users_ref.child(email.replace('.', ',')).get()

        if user_data:
            return cls(email=user_data['email'], password=user_data['password'])
        else:
            return None

    def __str__(self):
        return self.email

    class Meta:
        app_label = 'myapp' 