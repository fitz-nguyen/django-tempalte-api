from django.urls import include, path
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter

from apps.notification.api import views

router = DefaultRouter()
router.register(r"devices", FCMDeviceAuthorizedViewSet)

urlpatterns = [
    path("fcm/", include(router.urls)),
    path("", views.MessageListView.as_view(), name="messages"),
    path("read/", views.MessageReadView.as_view(), name="messages-read"),
    path("archive/", views.MessageArchiveView.as_view(), name="messages-archive"),
    path("badge/", views.MessageBadgeView.as_view(), name="messages-badge"),
]
