from celery import Celery
import os

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'progcomp')

# Create Celery app
app = Celery('progcomp')

# Load settings from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from installed Django apps
app.autodiscover_tasks()