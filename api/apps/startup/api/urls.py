from django.urls import path

from apps.startup.api import views

urlpatterns = [
    path("", views.StartupView.as_view(), name="startup"),
]
