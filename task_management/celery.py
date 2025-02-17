import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab


# Set the default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_management.settings')

app = Celery('task_management')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'


app.conf.beat_schedule = {
    'send-task-reminder-every-5-minutes': {
        'task': 'tasks.tasks.send_task_reminder',
        'schedule': crontab(minute='*/5'),  # This runs every 5 minutes
        'args': (),  # Add dynamic task_id here
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')