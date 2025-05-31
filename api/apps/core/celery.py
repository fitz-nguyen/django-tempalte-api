from __future__ import absolute_import, unicode_literals

import logging
import os

import logstash
from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger, after_setup_task_logger
from django.conf import settings


# Init logstash
def initialize_logstash(logger=None, loglevel=logging.INFO, **kwargs):
    handler = logstash.TCPLogstashHandler(
        settings.IP_LOGSTASH,
        settings.PORT_LOGSTASH,
        tags=["celery-logstash"],
        message_type="celery",
        version=1,
    )
    handler.setLevel(loglevel)
    logger.addHandler(handler)
    return logger


# Logstash
after_setup_task_logger.connect(initialize_logstash)
after_setup_logger.connect(initialize_logstash)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
app = Celery("app.core")

app.conf.ONCE = {
    "backend": "celery_once.backends.Redis",
    "settings": {"url": settings.BROKER_URL, "default_timeout": 60 * 60},
}

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Celery Request: {0!r}".format(self.request))


app.conf.beat_schedule = {
    # "periodic-generate-contact-data-task": {
    #     "task": "apps.dashboard.tasks.periodic_generate_contact_data_task",
    #     "schedule": crontab(minute=settings.MINUTES_RUN_UPDATE_DASHBOARD_CONTACT_DATA),
    #     "args": (),
    # },
    # "periodic-expired-invited-task": {
    #     "task": "apps.users.tasks.update_expired_invite",
    #     "schedule": crontab(minute=0, hour=0),
    #     "args": (),
    # },
    # "periodic-remove_upload_file": {
    #     "task": "apps.uploads.tasks.remove_upload_file",
    #     "schedule": crontab(hour=12),
    #     "args": (),
    # },
    # "periodic-update-import-contact-stuck-in-processing": {
    #     "task": "apps.dashboard.tasks.update_import_contact_stuck_in_processing",
    #     "schedule": crontab(hour=12),
    #     "args": (),
    # },
}
