"""
Ship Permissions (Presentation Layer)
Anti-IDOR and authorization rules for vessel resources.
"""

from rest_framework import permissions

class IsShipOwnerOrAdmin(permissions.BasePermission):
    """
    Anti-IDOR: Hanya pemilik sah kapal, admin, atau regulator yang dapat mengubah/menghapus kapal.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'role', '') in ('admin', 'superadmin', 'regulator') or user.is_staff or user.is_superuser:
            return True
        user_owner = getattr(user, 'owner', None)
        return user_owner is not None and obj.owner_id == user_owner.id
