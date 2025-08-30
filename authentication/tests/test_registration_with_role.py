from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class RegistrationWithRoleTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.registration_url = '/api/auth/register/'
        
        # Test data
        self.valid_registration_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
        }
        
        self.valid_registration_data_with_role = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'role': 'captain'
        }

    def test_registration_without_role_uses_default(self):
        """Test that registration without role uses 'owner' as default"""
        response = self.client.post(self.registration_url, self.valid_registration_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('username', response.data)
        
        # Check that user was created with default role
        user = User.objects.get(username='testuser')
        self.assertEqual(user.role, 'owner')

    def test_registration_with_role(self):
        """Test that registration with role uses the specified role"""
        response = self.client.post(self.registration_url, self.valid_registration_data_with_role, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('username', response.data)
        
        # Check that user was created with specified role
        user = User.objects.get(username='testuser2')
        self.assertEqual(user.role, 'captain')

    def test_registration_with_invalid_role_fails(self):
        """Test that registration with invalid role fails"""
        invalid_data = self.valid_registration_data.copy()
        invalid_data['username'] = 'testuser3'
        invalid_data['role'] = 'invalid_role'
        
        response = self.client.post(self.registration_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)