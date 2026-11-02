"""
Catch Permissions (Presentation Layer)
Anti-IDOR and ownership security validation for fish catch records.
"""

from rest_framework import permissions

class IsCatchOwnerOrAdmin(permissions.BasePermission):
    """
    Anti-IDOR: Hanya pemilik kapal, nahkoda kapal terkait, atau admin/regulator yang dapat mengubah/menghapus laporan tangkapan.
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
        catch_obj = getattr(obj, 'fish_catch', obj)
        ship = getattr(catch_obj, 'ship', None)
        if not ship:
            return False
        user_owner = getattr(user, 'owner', None)
        user_captain = getattr(user, 'captain', None)
        if user_owner and ship.owner_id == user_owner.id:
            return True
        if user_captain and ship.captain_id == user_captain.id:
            return True
        return False
