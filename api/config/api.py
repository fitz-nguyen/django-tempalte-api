from django.urls import include, path

urlpatterns = [
    path("users/", include("apps.users.api.urls")),
    path("", include("apps.users_auth.api.urls")),
    path("startup/", include("apps.startup.api.urls")),
    path("uploads/", include("apps.uploads.api.urls")),
    path("systems/", include("apps.systems.api.urls")),
    path("notifications/", include("apps.notification.api.urls")),
]
