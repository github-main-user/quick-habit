from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Validates if user in request is owner of the object."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
