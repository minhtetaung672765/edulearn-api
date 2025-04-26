from rest_framework import permissions

class IsEducatorOrReadOnly(permissions.BasePermission):
    """
    Allow educators full access. Others can only read.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.role == 'educator'