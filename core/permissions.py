from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role")
            and request.user.role.name == "admin"
            and request.user.status == 2
        )


class IsUser(BasePermission):
    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role")
            and request.user.role.name == "user"
            and request.user.status == 1
        )
