import os

from celery import Celery
from celery.schedules import crontab

app = Celery(
    'etl_tasks',
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL")
)


app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True
)

app.conf.beat_schedule = {
    'run_extract_tender_daily': {
        'task': 'src.tasks.extract_tender_task',
        'schedule': crontab(hour="0", minute="35")
    },
}

app.autodiscover_tasks(['src.tasks'])
