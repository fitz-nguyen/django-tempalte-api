from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.location.models import USLocationInfo


class ListStateView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        where = Q(state__isnull=False)
        search = self.request.query_params.get("search")
        if search:
            where &= Q(state__icontains=search)
        data = USLocationInfo.objects.filter(where).order_by("state").distinct("state").values_list("state", flat=True)
        return Response({"data": data})


class ListUSCitiesView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        where = Q(city__isnull=False)
        state_value = self.request.query_params.get("state")
        if state_value:
            where &= Q(state=state_value)
        search = self.request.query_params.get("search")
        if search:
            where &= Q(city__icontains=search)
        data = USLocationInfo.objects.filter(where).order_by("city").distinct("city").values_list("city", flat=True)
        return Response({"data": data})


class ListZipcodeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        where = Q()
        city = self.request.query_params.get("city")
        if city:
            where &= Q(city=city)
        state_value = self.request.query_params.get("state")
        if state_value:
            where &= Q(state=state_value)
        search = self.request.query_params.get("search")
        if search:
            where &= Q(zipcode__icontains=search)
        data = (
            USLocationInfo.objects.filter(where)
            .order_by("zipcode")
            .distinct("zipcode")
            .values_list("zipcode", flat=True)
        )
        return Response({"data": data})
