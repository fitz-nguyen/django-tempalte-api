from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.context import AppContext
from apps.startup.exceptions import PlatformNotFoundException
from apps.startup.models import AppVersion, Message


class StartupView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        update_app_message = Message.get_update_app_message()
        context = AppContext.instance()
        platform = self.request.query_params.get("platform", context.platform)
        app_version = AppVersion.get_app_version(platform)

        if app_version is None:
            raise PlatformNotFoundException

        data = {
            "update": {
                "minimal_version": app_version.minimal_version,
                "current_version": app_version.current_version,
                "platform": platform,
                "app_store_url": app_version.app_store_url,
                "title": update_app_message.title,
                "message": update_app_message.message,
                "icon": update_app_message.icon,
                "background": update_app_message.background,
            }
        }
        return Response(data, status=status.HTTP_200_OK)
