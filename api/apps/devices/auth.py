from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request

from apps.core import utils
from apps.devices.hash import hash_device_id
from apps.devices.models import DeviceInfo, UserDevice
from apps.users.models import User

logger = utils.get_logger()


class DeviceIDAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
        device_id = utils.get_device_id(request)
        if not device_id:
            return

        hashed_device_id = hash_device_id(device_id)
        device, _ = DeviceInfo.objects.get_or_create(
            device_id=hashed_device_id,
            platform=DeviceInfo.IOS,
            platform_version="12.0",
        )
        if not device:
            msg = "Invalid Device ID header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)

        user_device = UserDevice.objects.select_related("user").filter(device=device).first()
        if not user_device:
            associated_user_ids = UserDevice.objects.filter().values_list("user_id", flat=True)
            user = User.objects.all().exclude(pk__in=associated_user_ids).first()
            UserDevice.objects.create(user=user, device=device, in_use=True)
        else:
            user = user_device.user
        return user, device_id
