from apps.core.celery import app
from apps.uploads.models import UploadFile
from apps.uploads.services.usercases import UploadFileService
from apps.users.models import User
from apps.users.services import handle_post_save_user
from apps.users.settings import app_settings


@app.task(autoretry_for=(Exception,), max_retries=2)
def post_save_update_user_task(user_id: str, **kwargs):
    return handle_post_save_user(user_id)


@app.task(autoretry_for=(Exception,), max_retries=2)
def create_thumbnail_task(user_id: str, **kwargs):
    user = User.objects.get(pk=user_id)
    try:
        file_path = str(UploadFile.objects.filter(user=user).first().file_path)
    except Exception as e:
        print(e)
        return
    service = UploadFileService(user)
    size = (
        app_settings.THUMBNAIL_FILE_HEIGHT,
        app_settings.THUMBNAIL_FILE_WIDTH,
    )
    name_suffix = "x".join(map(str, size))
    thumbnail_path = service.create_thumbnail(file_path, name_suffix)
    user.avatar_thumb = thumbnail_path.get(name_suffix)
    user.save()
