"""
Celery Application Configuration
Handles asynchronous task processing for JatanCRM integration
"""

from celery import Celery
from celery.schedules import crontab
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Celery Configuration
broker_url = os.getenv(
    "CELERY_BROKER_URL",
    "pyamqp://admin:admin123@rabbitmq:5672//"
)
backend_url = os.getenv(
    "CELERY_BACKEND_URL",
    "redis://redis:6379/0"
)

# Create Celery app
celery = Celery(
    "jatan_salary_tasks",
    broker=broker_url,
    backend=backend_url,
    include=['tasks']  # Import tasks module
)

# Celery Configuration
celery.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Dubai',
    enable_utc=True,
    
    # Result backend settings
    result_backend=backend_url,
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes hard limit
    task_soft_time_limit=240,  # 4 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Queue settings
    task_routes={
        'tasks.sync_employees_to_crm': {'queue': 'crm_sync'},
        'tasks.sync_salaries_to_crm': {'queue': 'crm_sync'},
        'tasks.sync_reports_to_crm': {'queue': 'crm_sync'},
        'tasks.generate_monthly_report': {'queue': 'reports'},
        'tasks.backup_database': {'queue': 'maintenance'},
        'tasks.cleanup_old_files': {'queue': 'maintenance'},
    },
    
    # Retry settings
    task_default_retry_delay=60,  # Retry after 60 seconds
    task_max_retries=3,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'sync-crm-every-10-minutes': {
            'task': 'tasks.periodic_crm_sync',
            'schedule': crontab(minute='*/10'),  # Every 10 minutes
            'options': {'queue': 'crm_sync'}
        },
        'backup-database-daily': {
            'task': 'tasks.backup_database',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
            'options': {'queue': 'maintenance'}
        },
        'cleanup-old-files-weekly': {
            'task': 'tasks.cleanup_old_files',
            'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Sunday at 3 AM
            'options': {'queue': 'maintenance'}
        },
        'generate-monthly-reports': {
            'task': 'tasks.generate_monthly_report',
            'schedule': crontab(day_of_month=1, hour=1, minute=0),  # 1st of month at 1 AM
            'options': {'queue': 'reports'}
        },
    },
)

logger.info("Celery application configured successfully")
logger.info(f"Broker: {broker_url}")
logger.info(f"Backend: {backend_url}")

if __name__ == '__main__':
    celery.start()


