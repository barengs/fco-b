from django.contrib import admin
from .models import Role, UserRole, Menu, RoleMenu

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'assigned_at']
    list_filter = ['role', 'assigned_at']
    search_fields = ['user__username', 'role__name']

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'parent', 'order', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'url']
    ordering = ['order']

@admin.register(RoleMenu)
class RoleMenuAdmin(admin.ModelAdmin):
    list_display = ['role', 'menu', 'can_view', 'can_create', 'can_edit', 'can_delete']
    list_filter = ['role', 'menu', 'can_view', 'can_create', 'can_edit', 'can_delete']