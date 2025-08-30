import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append('/Users/ROFI/Develop/proyek/fco_project')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fco_project.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from owners.serializers import UserRegistrationSerializer

User = get_user_model()

def test_serializer():
    """Test the registration serializer"""
    print("Testing UserRegistrationSerializer...")
    
    # Valid data
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123',
        'password_confirm': 'testpassword123'
    }
    
    serializer = UserRegistrationSerializer(data=data)
    is_valid = serializer.is_valid()
    print(f"Serializer is valid: {is_valid}")
    
    if not is_valid:
        print(f"Errors: {serializer.errors}")
        return False
    
    # Create user
    user = serializer.save()
    print(f"User created: {user.username}")
    
    # Test password mismatch
    print("\nTesting password mismatch...")
    data['password_confirm'] = 'differentpassword'
    serializer = UserRegistrationSerializer(data=data)
    is_valid = serializer.is_valid()
    print(f"Serializer is valid with mismatched passwords: {is_valid}")
    
    if not is_valid:
        print(f"Expected error: {serializer.errors}")
        return True
    
    return False

if __name__ == '__main__':
    success = test_serializer()
    if success:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")