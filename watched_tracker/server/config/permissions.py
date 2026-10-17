from rest_framework.permissions import BasePermission


def user_is_admin(user):
    return bool(
        user
        and user.is_authenticated
        and user.role is not None
        and user.role.name.lower() == 'admin'
    )


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return user_is_admin(request.user)
