from apps.systems import choices
from apps.systems.api.serializers import PageConfigParamSerializer, PageConfigSerializer, SystemConfigSerializer
from apps.systems.exceptions import SystemConfigNotSetException
from apps.systems.models import PageConfig, SystemConfig
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class PageContentAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(query_serializer=PageConfigParamSerializer)
    def get(self, request):
        content_type = request.query_params.get("type", "")
        if not content_type:
            content_type = choices.LEARN_MORE_WEB
        page = PageConfig.objects.filter(type=content_type, published=True).first()
        if page:
            return Response(PageConfigSerializer(instance=page).data)
        raise SystemConfigNotSetException()


class SystemConfigView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SystemConfigSerializer

    def get_object(self):
        return SystemConfig.objects.first()
