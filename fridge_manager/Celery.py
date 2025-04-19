from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fridge_manager.settings')

app = Celery('fridge_manager')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'check-expiration-daily': {
        'task': 'inventory.tasks.check_item_expiration',  
        'schedule': crontab(hour=0, minute=0),  
    },
}
