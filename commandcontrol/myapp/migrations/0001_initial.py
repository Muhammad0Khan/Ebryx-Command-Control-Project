# Generated by Django 4.2.7 on 2023-12-21 09:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='APIToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=40, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CPUInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('cpu_count', models.IntegerField()),
                ('cpu_percent', models.FloatField()),
                ('cpu_freq_value', models.FloatField()),
                ('threads', models.IntegerField()),
                ('per_cpu_percent', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='InstalledApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=50)),
                ('data', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='RemoteCPUInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remote_ip', models.GenericIPAddressField()),
                ('pc_name', models.CharField(blank=True, max_length=255, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('cpu_count', models.IntegerField()),
                ('cpu_percent', models.FloatField()),
                ('cpu_freq_value', models.FloatField()),
                ('threads', models.IntegerField()),
                ('per_cpu_percent', models.JSONField()),
                ('status', models.CharField(choices=[('Online', 'Online'), ('Offline', 'Offline')], default='Online', max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
