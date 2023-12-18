from rest_framework import serializers
from .models import InstalledApp

class InstalledAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstalledApp
        fields = '__all__'