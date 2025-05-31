from datetime import datetime, timedelta

from celery.schedules import crontab

from apps.core.celery import app
from apps.uploads.enums import FileState
from apps.uploads.models import UploadFile
from apps.uploads.settings import app_settings as settings


# run_every = crontab(hour=12)
@app.task(autoretry_for=(Exception,), max_retries=2)
def remove_upload_file():
    print("Automated Delete Record File Not Used Task is end ....")
    time_space = datetime.now() - timedelta(hours=settings.TIME_TO_DELETE_UPLOAD_FILE)
    UploadFile.objects.filter(status=FileState.NEW, created__lt=time_space).delete()
    print("Automated Delete Record File Not Used Task is successfully ....")
