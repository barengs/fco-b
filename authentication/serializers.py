from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from owners.models import Owner, Captain
from ships.models import Ship
from admin_module.models import AdminProfile
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=getattr(User, 'USER_ROLE_CHOICES', []),
        required=False
    )
    full_name = serializers.CharField(max_length=200, required=False)
    contact_info = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    ship_code = serializers.CharField(max_length=100, required=False, allow_blank=True, write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'role', 
                  'full_name', 'contact_info', 'address', 'phone', 'ship_code')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")

        # Allow self-registration for owner, captain, and admin
        allowed_roles = ['owner', 'captain', 'admin']
        role = attrs.get('role', 'owner')  # Default to owner if not provided

        if role not in allowed_roles:
            raise serializers.ValidationError(
                f"Self-registration hanya diperbolehkan untuk role: {', '.join(allowed_roles)}. "
                f"Untuk role lain (regulator), silakan hubungi administrator."
            )

        return attrs
    
    def create(self, validated_data):
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        
        # Extract profile data
        full_name = validated_data.pop('full_name', '')
        contact_info = validated_data.pop('contact_info', '')
        address = validated_data.pop('address', '')
        phone = validated_data.pop('phone', '')
        ship_code = validated_data.pop('ship_code', None)
        
        # Set default role if not provided
        if 'role' not in validated_data or not validated_data['role']:
            validated_data['role'] = 'owner'

        # Double-check role is allowed (safety measure)
        role = validated_data.get('role', 'owner')
        if role not in ['owner', 'captain', 'admin']:
            raise serializers.ValidationError(f"Role '{role}' tidak diperbolehkan untuk self-registration")

        # Create user with hashed password
        user = User.objects.create_user(**validated_data)

        # Create related profile based on role
        if role == 'owner':
            # Create owner profile
            owner = Owner._default_manager.create(  # type: ignore
                full_name=full_name or validated_data.get('username', ''),
                owner_type='individual',  # Default to individual
                contact_info=contact_info,
                email=validated_data.get('email', ''),
                phone=phone,
                address=address
            )
            user.owner = owner
            user.save()
            
            # If ship code is provided, update the ship with this owner
            if ship_code:
                try:
                    ship = Ship._default_manager.get(registration_number=ship_code)  # type: ignore
                    ship.owner = owner
                    ship.save()
                except Ship._default_manager.model.DoesNotExist:
                    # Log the error but don't fail registration
                    pass
                    
        elif role == 'captain':
            # For captains, we would typically link to an existing owner
            # But for registration, we'll create a placeholder owner
            owner = Owner._default_manager.create(  # type: ignore
                full_name=f"Owner of {full_name}" if full_name else f"Owner of {validated_data.get('username', '')}",
                owner_type='individual',
                contact_info=contact_info,
                email=validated_data.get('email', ''),
                phone=phone,
                address=address
            )
            # Create captain profile
            captain = Captain._default_manager.create(  # type: ignore
                full_name=full_name or validated_data.get('username', ''),
                license_number=f"LIC{user.id}",  # Placeholder license number
                owner=owner,
                user=user,
                contact_info=contact_info,
                email=validated_data.get('email', ''),
                phone=phone,
                address=address
            )
            user.captain = captain
            user.save()
            
            # If ship code is provided, update the ship with this captain
            if ship_code:
                try:
                    ship = Ship._default_manager.get(registration_number=ship_code)  # type: ignore
                    ship.captain = captain
                    ship.save()
                except Ship._default_manager.model.DoesNotExist:
                    # Log the error but don't fail registration
                    pass

        elif role == 'admin':
            # Create admin profile
            admin_profile = AdminProfile._default_manager.create(  # type: ignore
                user=user,
                full_name=full_name or validated_data.get('username', ''),
                email=validated_data.get('email', ''),
                phone=phone,
                department='Administrator',  # Default department
                position='Administrator'    # Default position
            )
            # Set user as staff and superuser
            user.is_staff = True
            user.is_superuser = True
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication token"""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )