from django.urls import path

from apps.users.api import views

urlpatterns = [
    path("me/", views.UserProfileView.as_view(), name="me"),
    path("delete/", views.DeleteUserView.as_view(), name="delete"),
    path("sales-representative/", views.SalesRepresentativeListView.as_view(), name="sales-representative"),
    path("regular-users/", views.RegularUserListView.as_view(), name="regular-users"),
    path("<uuid:user_id>/", views.UserDetailView.as_view(), name="user-detail"),
    path(
        "profile/",
        views.UpdateUserProfileView.as_view(),
        name="update-profile",
    ),
    path("exists/", views.UserExistView.as_view(), name="user-exists"),
    path("impersonate/<uuid:user_id>/", views.impersonate_user_view, name="impersonate_user"),
    path("companies/", views.ActiveCompanyListView.as_view(), name="companies"),
]
