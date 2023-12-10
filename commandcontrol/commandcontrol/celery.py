from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "commandcontrol.settings")

# Create a Celery instance and configure it using the settings of the Django project
app = Celery("commandcontrol")

# Load tasks modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Automatically discover tasks in all registered Django app configs.
app.autodiscover_tasks()
