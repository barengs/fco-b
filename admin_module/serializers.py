from rest_framework import serializers
from .models import Role, UserRole, Menu, RoleMenu, AdminProfile
from owners.models import CustomUser


class RegulatorRegistrationSerializer(serializers.Serializer):
    """Serializer for regulator registration by admin"""
    username = serializers.CharField(
        max_length=150,
        help_text="Username untuk regulator (harus unik)"
    )
    email = serializers.EmailField(
        help_text="Email regulator (harus unik)"
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Password untuk regulator (minimal 8 karakter)"
    )
    full_name = serializers.CharField(
        max_length=200,
        help_text="Nama lengkap regulator"
    )
    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text="Nomor telepon regulator"
    )
    department = serializers.CharField(
        max_length=100,
        required=False,
        default="Regulator",
        help_text="Departemen regulator (default: Regulator)"
    )
    position = serializers.CharField(
        max_length=100,
        required=False,
        default="Regulator Kuota",
        help_text="Posisi regulator (default: Regulator Kuota)"
    )

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username sudah digunakan")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email sudah digunakan")
        return value


class RegulatorRegistrationResponseSerializer(serializers.Serializer):
    """Response serializer for regulator registration"""
    message = serializers.CharField(help_text="Pesan sukses pendaftaran")
    user_id = serializers.IntegerField(help_text="ID pengguna yang dibuat")
    username = serializers.CharField(help_text="Username regulator")
    role = serializers.CharField(help_text="Role pengguna")
    full_name = serializers.CharField(help_text="Nama lengkap regulator")
    email = serializers.EmailField(help_text="Email regulator")
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
    
    # Role field - allow selection of admin roles
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role._default_manager.all(),
        required=False,
        help_text="Select a specific admin role for this user",
        allow_null=True
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'full_name', 'phone', 'department', 'position', 'role']
    
    def create(self, validated_data):
        # Extract profile data
        profile_data = {
            'full_name': validated_data.pop('full_name', None),
            'email': validated_data.pop('email', None),
            'phone': validated_data.pop('phone', None),
            'department': validated_data.pop('department', None),
            'position': validated_data.pop('position', None),
        }
        
        # Extract role data
        selected_role = validated_data.pop('role', None)
        
        # Create the user
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            role='admin'  # Set base role to admin
        )
        
        # Create the admin profile
        AdminProfile(user=user, **{k: v for k, v in profile_data.items() if v}).save()
        
        # Assign the specific role to the user if provided
        if selected_role:
            # Use get_or_create to assign the role
            UserRole._default_manager.get_or_create(
                user=user,
                role=selected_role
            )
        
        return user
