"""
Celery configuration for Photo Album application.
Handles background task processing for AI photo/video analysis.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_album.settings')

app = Celery('photo_album')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure task time limits
# AI processing can take longer, especially on CPU without GPU
# Increased significantly for CPU-only servers
app.conf.task_time_limit = 600  # 10 minutes hard limit
app.conf.task_soft_time_limit = 540  # 9 minutes soft limit (raises exception)

# Configure Celery Beat schedule for automatic processing
app.conf.beat_schedule = {
    'process-pending-photos-daily': {
        'task': 'album.tasks.process_pending_photos_batch',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'process-pending-videos-daily': {
        'task': 'album.tasks.process_pending_videos_batch',
        'schedule': crontab(hour=2, minute=30),  # 2:30 AM daily
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f'Request: {self.request!r}')


# Pre-load AI models when worker starts
from celery.signals import worker_process_init
import logging

logger = logging.getLogger(__name__)


@worker_process_init.connect
def init_worker_process(sender=None, **kwargs):
    """
    Initialize worker process by pre-loading AI models.
    This runs once per worker process, significantly improving performance.
    """
    logger.info("Initializing worker process - pre-loading AI models...")
    try:
        from album.services.ai_analysis_service import ai_analysis_service
        # Trigger model loading by checking availability
        if ai_analysis_service.is_available():
            logger.info("AI models successfully pre-loaded in worker process")
        else:
            logger.warning("AI models not available in this worker")
    except Exception as e:
        logger.error(f"Failed to pre-load AI models in worker: {e}")
