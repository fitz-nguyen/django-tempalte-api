from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import DestroyAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import ObjectNotFoundException
from apps.users import choices, services
from apps.users.api import serializers
from apps.users.choices import REGULAR, SALE
from apps.users.models import Company, ResetPasswordOTP, User
from apps.users.permissions import IsAdminUser
from apps.users.token import CustomImpersonalAccessToken


def impersonate_user_view(request, user_id):
    if not request.user:
        return HttpResponse("Unauthorized", status=401)
    # TODO: check why it not working on staging
    # if not request.user.is_staff or not request.user.is_superuser:
    #    return HttpResponse("Unauthorized", status=401)
    user = get_object_or_404(User, id=user_id)
    serializer = CustomImpersonalAccessToken.for_user(user)
    url = str(settings.FRONTEND_BASE_URL).rstrip("/") + f"?impersonate=True&token={str(serializer)}"
    return redirect(url)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = serializers.UserProfileSerializer

    def get_object(self):
        return self.request.user


class SalesRepresentativeListView(generics.ListAPIView):
    serializer_class = serializers.UserSimpleInfoSerializer

    def get_queryset(self):
        queryset = User.objects.filter(
            role=SALE, company_id=self.request.user.company_id, status=choices.APPROVED, is_active=True
        )

        # Search using Q objects
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(email__icontains=search) | Q(display_name__icontains=search))

        return queryset.order_by("display_name")


class RegularUserListView(generics.ListAPIView):
    serializer_class = serializers.UserSimpleInfoSerializer

    def get_queryset(self):
        queryset = User.objects.filter(
            role=REGULAR, company_id=self.request.user.company_id, status=choices.APPROVED, is_active=True
        )

        # Search using Q objects
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(email__icontains=search) | Q(display_name__icontains=search))

        return queryset.order_by("display_name")


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.UserProfileSerializer

    def get_object(self):
        try:
            user_id = self.kwargs.get("user_id")
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ObjectNotFoundException("There is no user that matches with this id.")


class UpdateUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.UserProfileSerializer

    def get_object(self):
        return self.request.user


class UserExistView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="check exist email,username or phone",
        operation_id="username_email_phone_exist",
        security=[],
    )
    def get(self, request, *args, **kwargs):
        username = request.query_params.get("username")
        email = request.query_params.get("email")
        phone = request.query_params.get("phone")

        exists = services.exists_user(username=username, email=email, phone=phone)

        data = {"exists": exists}
        return Response(data, status=status.HTTP_200_OK)


class DeleteUserView(DestroyAPIView):
    """Deletes the user info cancel subscription and relations"""

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        # Delete PROTECT relation
        ResetPasswordOTP.objects.filter(user=user).delete()
        user.delete()
        return Response({"detail": "success"})


class ActiveCompanyListView(generics.ListAPIView):
    """List all companies"""

    serializer_class = serializers.CompanyListSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return Company.objects.order_by("business_name")
