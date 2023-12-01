from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # add additional fields here
    def __str__(self):
        return self.user.username
