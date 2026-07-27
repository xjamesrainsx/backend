from celery import Celery
from celery.schedules import crontab
from config.settings import settings

celery_app = Celery("ingestion_workers", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Automated cron schedules maintaining local repository freshness
celery_app.conf.beat_schedule = {
    "periodic-data-reconciliation-every-5-minutes": {
        "task": "workers.tasks.fetch_periodic_data",
        "schedule": crontab(minute="*/5"),
    },
}

celery_app.autodiscover_tasks(["workers"])
