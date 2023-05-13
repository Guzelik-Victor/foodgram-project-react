from rest_framework.permissions import SAFE_METHODS, BasePermission


class SafeMethodOrAuthUserPermission(BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )


class AdminOrReadOnly(SafeMethodOrAuthUserPermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_staff
        )


class OwnerOrReadOnly(SafeMethodOrAuthUserPermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user == obj.author
            or request.user.is_staff
        )
