from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

celery = Celery()
celery.config_from_object("django.conf:settings", namespace="CELERY")

# Clean up older tasks for a Fresh Start
celery.control.purge()

celery.autodiscover_tasks()
