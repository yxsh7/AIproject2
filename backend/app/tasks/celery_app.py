"""Celery application configuration"""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

# Create Celery app
celery_app = Celery(
    "devmetrics",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.sync_tasks",
        "app.tasks.analysis_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic task schedule (Celery Beat)
celery_app.conf.beat_schedule = {
    # Sync GitHub every 2 hours
    "sync-github-every-2-hours": {
        "task": "app.tasks.sync_tasks.sync_all_github",
        "schedule": crontab(minute=0, hour="*/2"),
    },
    # Sync Jira every 3 hours
    "sync-jira-every-3-hours": {
        "task": "app.tasks.sync_tasks.sync_all_jira",
        "schedule": crontab(minute=0, hour="*/3"),
    },
    # Run AI analysis every 4 hours
    "analyze-activities-every-4-hours": {
        "task": "app.tasks.analysis_tasks.analyze_all_unanalyzed",
        "schedule": crontab(minute=0, hour="*/4"),
    },
}

if __name__ == "__main__":
    celery_app.start()
