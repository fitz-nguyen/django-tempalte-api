from django.urls import path

from apps.location.api.views import ListStateView, ListUSCitiesView, ListZipcodeView

urlpatterns = [
    path("us/states/", ListStateView.as_view(), name="states"),
    path("us/cities/", ListUSCitiesView.as_view(), name="cities-state"),
    path("us/zipcode/", ListZipcodeView.as_view(), name="cities-state"),
]
