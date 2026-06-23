from rest_framework.permissions import BasePermission
from .models import UserProfile


class IsMaster(BasePermission):
    message = "Apenas Mestres de Mesa podem realizar esta ação."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == UserProfile.ROLE_MASTER
        )


class IsPlayer(BasePermission):
    message = "Apenas Jogadores podem realizar esta ação."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == UserProfile.ROLE_PLAYER
        )
