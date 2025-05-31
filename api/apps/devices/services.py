from typing import Optional

from cache_memoize import cache_memoize

from apps.core import utils
from apps.devices.hash import hash_device_id
from apps.devices.models import DeviceInfo, UserDevice


def track_user_device(request) -> Optional[UserDevice]:
    try:
        if not request.user or not request.user.is_authenticated:
            return None
        user = request.user
        device_id = utils.get_device_id(request)
        if not device_id:
            return None

        platform = utils.get_platform(request)
        platform_version = utils.get_platform_version(request)
        app_version = utils.get_app_version(request=request)
        hashed_device_id = hash_device_id(device_id)
        device = get_device(hashed_device_id, platform_version, platform, app_version)
        if not device:
            device = update_or_create_device(hashed_device_id, platform_version, platform, app_version)
        user_device = UserDevice.objects.filter(user=user, device=device).first()
        if not user_device:
            user_device = UserDevice.objects.create(user=user, device=device)
        return user_device
    except Exception as ex:
        utils.get_logger(__name__).exception(ex)
        return None


@cache_memoize(60 * 60)
def get_device(hashed_device_id: str, platform_version: str, platform: str, app_version: str) -> Optional[DeviceInfo]:
    return DeviceInfo.objects.filter(
        device_id=hashed_device_id,
        platform_version=platform_version,
        platform=platform,
        app_version=app_version,
    ).first()


def update_or_create_device(
    hashed_device_id: str, platform_version: str, platform: str, app_version: str
) -> DeviceInfo:
    device, _ = DeviceInfo.objects.update_or_create(
        device_id=hashed_device_id,
        defaults={
            "platform": platform,
            "platform_version": platform_version,
            "app_version": app_version,
        },
    )
    return device


@cache_memoize(60 * 60)
def get_user_device(device: DeviceInfo) -> Optional[UserDevice]:
    return UserDevice.objects.select_related("user").filter(device=device).first()
