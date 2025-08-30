from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Owner, Captain

User = get_user_model()

class OwnerSerializer(serializers.ModelSerializer):
    """Serializer for Owner with related ships and captains"""
    ships = serializers.SerializerMethodField()
    captains = serializers.SerializerMethodField()
    
    class Meta:
        model = Owner
        fields = '__all__'
    
    def get_ships(self, obj):
        """Get ships associated with this owner"""
        ships = obj.ships.all()
        # Return basic ship information to avoid circular imports
        return [
            {
                'id': ship.id,
                'name': ship.name,
                'registration_number': ship.registration_number,
                'active': ship.active
            }
            for ship in ships
        ]
    
    def get_captains(self, obj):
        """Get captains associated with this owner"""
        captains = obj.captains.all()
        # Return basic captain information
        return [
            {
                'id': captain.id,
                'name': captain.name,
                'license_number': captain.license_number
            }
            for captain in captains
        ]

class CaptainSerializer(serializers.ModelSerializer):
    """Serializer for Captain with related ships and owner"""
    ships = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    
    class Meta:
        model = Captain
        fields = '__all__'
    
    def get_ships(self, obj):
        """Get ships operated by this captain"""
        ships = obj.ships.all()
        # Return basic ship information to avoid circular imports
        return [
            {
                'id': ship.id,
                'name': ship.name,
                'registration_number': ship.registration_number,
                'active': ship.active
            }
            for ship in ships
        ]

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    def create(self, validated_data):
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        
        # Create user with hashed password
        user = User.objects.create_user(**validated_data)
        return user