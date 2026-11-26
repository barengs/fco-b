"""
Ship Permissions (Presentation Layer)
Anti-IDOR and authorization rules for vessel resources.
"""

from rest_framework import permissions

class IsShipOwnerOrAdmin(permissions.BasePermission):
    """
    Anti-IDOR: Hanya pemilik sah kapal, nahkoda kapal, admin, atau regulator yang dapat mengakses/mengubah kapal.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'role', '') in ('admin', 'superadmin', 'regulator') or user.is_staff or user.is_superuser:
            return True
        user_owner = getattr(user, 'owner', None)
        if user_owner is not None and obj.owner_id == user_owner.id:
            return True
        if request.method in permissions.SAFE_METHODS:
            user_captain = getattr(user, 'captain', None)
            return user_captain is not None and obj.captain_id == user_captain.id
        return False
