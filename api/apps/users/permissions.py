from rest_framework import permissions

from apps.users.choices import ADMIN, REGULAR, SALE


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow super admin or staff admin to access the view.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated and is either superuser or staff
        return bool(
            request.user and request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)
        )


class IsRegularUserOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow regular users or admins to access the view.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated and is either regular user or admin
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == REGULAR or request.user.role == ADMIN)
        )


class IsRegularUserOrAdminOrSale(permissions.BasePermission):
    """
    Custom permission to allow regular users, admins, or sale users to access the view.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated and is either regular user, admin, or sale
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == REGULAR or request.user.role == ADMIN or request.user.role == SALE)
        )
