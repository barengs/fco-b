from rest_framework import serializers
from .models import Role, UserRole, Menu, RoleMenu
from owners.models import CustomUser
from django.contrib.auth.models import Permission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permissions_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), 
        many=True, 
        write_only=True,
        source='permissions'
    )
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'permissions_ids', 'created_at', 'updated_at']

class UserRoleSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    role = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'assigned_at']

class MenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Menu
        fields = ['id', 'name', 'url', 'icon', 'parent', 'order', 'is_active', 'children', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        # Return serialized children
        children = obj.children.filter(is_active=True)
        return MenuSerializer(children, many=True, context=self.context).data

class RoleMenuSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)
    menu = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = RoleMenu
        fields = ['id', 'role', 'menu', 'can_view', 'can_create', 'can_edit', 'can_delete', 'assigned_at']