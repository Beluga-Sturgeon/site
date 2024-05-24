# celeryconfig.py

from celery.schedules import crontab

# Other configurations...

app.conf.beat_schedule = {
    'daily-get-daily': {
        'task': 'tasks.get_daily',
        'schedule': crontab(hour=9, minute=0),
    },
}
