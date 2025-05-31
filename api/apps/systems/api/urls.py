from apps.systems.api import views
from django.urls import path

urlpatterns = [
    path("pages/", views.PageContentAPIView.as_view(), name="system page config"),
    path("config/", views.SystemConfigView.as_view(), name="system page config"),
]
