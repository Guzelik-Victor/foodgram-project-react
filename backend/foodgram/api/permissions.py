from rest_framework.permissions import SAFE_METHODS, BasePermission


class SafeMethodOrAuthUserPermission(BasePermission):
    """Доступ пользователям при безопастном запросе
    или аутенфицированным."""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )


class AdminOrReadOnly(SafeMethodOrAuthUserPermission):
    """Доступ к объекту только с правами не ниже администратора."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_staff
        )


class OwnerOrReadOnly(SafeMethodOrAuthUserPermission):
    """Доступ к объекту только его создателю или администратору."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user == obj.author
            or request.user.is_staff
        )
