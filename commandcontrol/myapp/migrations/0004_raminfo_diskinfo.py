# Generated by Django 4.1.13 on 2024-05-20 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_remove_cpuinfo_hostname_remove_cpuinfo_system_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RamInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_memory', models.FloatField()),
                ('timestamp', models.DateTimeField()),
                ('available_memory', models.FloatField()),
                ('used_memory', models.FloatField()),
                ('free_memory', models.FloatField()),
                ('percent_memory', models.FloatField()),
                ('total_swap', models.FloatField()),
                ('used_swap', models.FloatField()),
                ('free_swap', models.FloatField()),
                ('percent_swap', models.FloatField()),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.apitoken')),
            ],
        ),
        migrations.CreateModel(
            name='DiskInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_disk', models.FloatField()),
                ('timestamp', models.DateTimeField()),
                ('used_disk', models.FloatField()),
                ('free_disk', models.FloatField()),
                ('percent_disk', models.FloatField()),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.apitoken')),
            ],
        ),
    ]
