from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forex_trading_project.settings')

app = Celery('forex_trading_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'fetch-and-save-market-data-every-minute': {
        'task': 'trading.tasks.fetch_and_save_market_data_task',
        'schedule': crontab(minute='*/1'),  # every minute
    },
}

# Use solo pool for compatibility with Windows
app.conf.worker_pool = 'solo'