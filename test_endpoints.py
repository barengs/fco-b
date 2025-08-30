import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append('/Users/ROFI/Develop/proyek/fco_project')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fco_project.settings')
django.setup()

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, force_authenticate
from rest_framework.authtoken.models import Token
from owners.views import RegistrationViewSet, CustomAuthToken
from owners.serializers import UserRegistrationSerializer
import json

User = get_user_model()

class EndpointTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()
        
    def test_registration_serializer(self):
        """Test the registration serializer"""
        # Valid data
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Test password mismatch
        data['password_confirm'] = 'differentpassword'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
    def test_registration_view(self):
        """Test the registration view"""
        view = RegistrationViewSet.as_view({'post': 'register'})
        
        # Valid registration
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        
        request = self.factory.post('/api/owners/auth/register/', data=json.dumps(data), content_type='application/json')
        response = view(request)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('username', response.data)
        
        # Check that user was created
        user_exists = User.objects.filter(username='testuser').exists()
        self.assertTrue(user_exists)
        
    def test_login_view(self):
        """Test the login view"""
        # First create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Test login
        view = CustomAuthToken.as_view()
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        request = self.factory.post('/api/owners/login/', data=json.dumps(data), content_type='application/json')
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('is_owner', response.data)
        self.assertIn('is_captain', response.data)

if __name__ == '__main__':
    import unittest
    unittest.main()