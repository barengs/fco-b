from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from owners.models import Owner, Captain
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
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'role', 
                  'full_name', 'contact_info', 'address', 'phone')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    def create(self, validated_data):
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        
        # Extract profile data
        full_name = validated_data.pop('full_name', '')
        contact_info = validated_data.pop('contact_info', '')
        address = validated_data.pop('address', '')
        phone = validated_data.pop('phone', '')
        
        # Set default role if not provided
        if 'role' not in validated_data or not validated_data['role']:
            validated_data['role'] = 'owner'
        
        # Create user with hashed password
        user = User.objects.create_user(**validated_data)
        
        # Create related profile based on role
        role = validated_data.get('role', 'owner')
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
        
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication token"""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )