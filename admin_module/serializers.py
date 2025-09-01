from rest_framework import serializers
from .models import Role, UserRole, Menu, RoleMenu, AdminProfile
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

class AdminUserSerializer(serializers.ModelSerializer):
    admin_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'admin_profile']
    
    def get_admin_profile(self, obj):
        try:
            profile = obj.admin_profile
            return {
                'full_name': profile.full_name,
                'email': profile.email,
                'phone': profile.phone,
                'department': profile.department,
                'position': profile.position
            }
        except AttributeError:
            return None


class AdminRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for admin user registration with profile"""
    # User fields
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=False)
    
    # Profile fields
    full_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    position = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'full_name', 'phone', 'department', 'position']
    
    def create(self, validated_data):
        # Extract profile data
        profile_data = {
            'full_name': validated_data.pop('full_name', None),
            'email': validated_data.pop('email', None),
            'phone': validated_data.pop('phone', None),
            'department': validated_data.pop('department', None),
            'position': validated_data.pop('position', None),
        }
        
        # Create the user
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            role='admin'  # Set role to admin
        )
        
        # Create the admin profile
        AdminProfile(user=user, **{k: v for k, v in profile_data.items() if v}).save()
        
        return user
