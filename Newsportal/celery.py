import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Newsportal.settings')

app = Celery('Newsportal')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_weekly_newsletters': {
        'task': 'news.tasks.send_weekly_newsletters',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Понедельник в 8 утра
        'options': {
            'expires': 60 * 60 * 24,
        },
    },
}