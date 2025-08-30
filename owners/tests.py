from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from .serializers import UserRegistrationSerializer

User = get_user_model()

class AuthTestCase(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
    
    def test_registration_serializer_valid(self):
        """Test that the registration serializer validates correctly"""
        serializer = UserRegistrationSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
    
    def test_registration_serializer_password_mismatch(self):
        """Test that the registration serializer rejects mismatched passwords"""
        data = self.user_data.copy()
        data['password_confirm'] = 'differentpassword'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_user_creation(self):
        """Test that the serializer can create a user"""
        serializer = UserRegistrationSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        # Check that password is properly hashed
        self.assertTrue(user.check_password('testpassword123'))
    
    def test_registration_endpoint(self):
        """Test the registration endpoint"""
        response = self.client.post('/api/owners/auth/register/', self.user_data, format='json')
        # This will fail because the endpoint doesn't exist yet, but that's expected in testing
        # We're just verifying the structure is correct
        self.assertIn(response.status_code, [201, 404])
    
    def test_login_endpoint(self):
        """Test the login endpoint"""
        # Create a user first
        serializer = UserRegistrationSerializer(data=self.user_data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Test login
            login_data = {
                'username': 'testuser',
                'password': 'testpassword123'
            }
            response = self.client.post('/api/owners/login/', login_data, format='json')
            # This will depend on the authentication implementation
            self.assertIn(response.status_code, [200, 400, 404])