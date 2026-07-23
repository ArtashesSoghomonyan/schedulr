from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return not request.user or not request.user.is_authenticated

class IsVerified(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_verified
