from django.utils.deprecation import MiddlewareMixin

from apps.devices.services import track_user_device


class DeviceIDLoggerMiddleware(MiddlewareMixin):
    @classmethod
    def process_response(cls, request, response):
        track_user_device(request=request)
        return response
