from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Owner, CustomUser, Captain

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_type', 'email', 'phone', 'created_at')
    list_filter = ('owner_type', 'created_at')
    search_fields = ('name', 'email', 'phone')
    ordering = ('name',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'owner')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Owner Information', {'fields': ('owner',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Owner Information', {
            'fields': ('owner',),
        }),
    )

@admin.register(Captain)
class CaptainAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_number', 'owner', 'email', 'phone', 'years_of_experience')
    list_filter = ('owner', 'years_of_experience', 'created_at')
    search_fields = ('name', 'license_number', 'email', 'phone')
    ordering = ('name',)
    raw_id_fields = ('owner', 'user')