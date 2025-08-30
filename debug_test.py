import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fco_project.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

User = get_user_model()

def test_registration_endpoint():
    """Test the registration endpoint"""
    client = APIClient()
    
    # Test data
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123',
        'password_confirm': 'testpassword123'
    }
    
    print("Testing user registration...")
    try:
        response = client.post('/api/owners/auth/register/', user_data, format='json')
        print(f"Registration response status: {response.status_code}")
        print(f"Registration response data: {response.data}")
        
        if response.status_code == 201:
            print("Registration successful!")
            
            # Test login
            print("\nTesting user login...")
            login_data = {
                'username': 'testuser',
                'password': 'testpassword123'
            }
            response = client.post('/api/owners/login/', login_data, format='json')
            print(f"Login response status: {response.status_code}")
            print(f"Login response data: {response.data}")
            
            if response.status_code == 200:
                print("Login successful!")
            else:
                print("Login failed!")
        else:
            print("Registration failed!")
            print(f"Errors: {response.data}")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_registration_endpoint()