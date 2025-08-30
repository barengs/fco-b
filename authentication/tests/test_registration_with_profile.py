from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status

User = get_user_model()


class RegistrationWithProfileTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.registration_url = '/api/auth/register/'
        
        # Test data for owner registration
        self.owner_registration_data = {
            'username': 'testowner',
            'email': 'owner@test.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'role': 'owner',
            'full_name': 'Test Owner',
            'contact_info': 'Contact info for owner',
            'address': '123 Owner Street',
            'phone': '1234567890'
        }
        
        # Test data for captain registration
        self.captain_registration_data = {
            'username': 'testcaptain',
            'email': 'captain@test.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'role': 'captain',
            'full_name': 'Test Captain',
            'contact_info': 'Contact info for captain',
            'address': '456 Captain Street',
            'phone': '0987654321'
        }

    def test_owner_registration_with_profile(self):
        """Test owner registration with profile information"""
        response = self.client.post(self.registration_url, self.owner_registration_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('role', response.data)
        self.assertEqual(response.data['role'], 'owner')
        self.assertIn('profile', response.data)
        self.assertEqual(response.data['profile']['type'], 'owner')
        self.assertEqual(response.data['profile']['full_name'], 'Test Owner')
        self.assertEqual(response.data['profile']['contact_info'], 'Contact info for owner')
        self.assertEqual(response.data['profile']['address'], '123 Owner Street')
        self.assertEqual(response.data['profile']['phone'], '1234567890')
        
        # Verify user and owner were created
        user = User.objects.get(username='testowner')
        self.assertEqual(user.role, 'owner')
        self.assertIsNotNone(user.owner)
        self.assertEqual(user.owner.full_name, 'Test Owner')
        self.assertEqual(user.owner.contact_info, 'Contact info for owner')
        self.assertEqual(user.owner.address, '123 Owner Street')
        self.assertEqual(user.owner.phone, '1234567890')

    def test_captain_registration_with_profile(self):
        """Test captain registration with profile information"""
        response = self.client.post(self.registration_url, self.captain_registration_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('role', response.data)
        self.assertEqual(response.data['role'], 'captain')
        self.assertIn('profile', response.data)
        self.assertEqual(response.data['profile']['type'], 'captain')
        self.assertEqual(response.data['profile']['full_name'], 'Test Captain')
        self.assertEqual(response.data['profile']['contact_info'], 'Contact info for captain')
        self.assertEqual(response.data['profile']['address'], '456 Captain Street')
        self.assertEqual(response.data['profile']['phone'], '0987654321')
        self.assertIn('license_number', response.data['profile'])
        
        # Verify user and captain were created
        user = User.objects.get(username='testcaptain')
        self.assertEqual(user.role, 'captain')
        self.assertIsNotNone(user.captain)
        self.assertEqual(user.captain.full_name, 'Test Captain')
        self.assertEqual(user.captain.contact_info, 'Contact info for captain')
        self.assertEqual(user.captain.address, '456 Captain Street')
        self.assertEqual(user.captain.phone, '0987654321')

    def test_registration_without_profile_data_uses_defaults(self):
        """Test registration without profile data uses defaults"""
        minimal_data = {
            'username': 'minimaluser',
            'email': 'minimal@test.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'role': 'owner'
        }
        
        response = self.client.post(self.registration_url, minimal_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('profile', response.data)
        self.assertEqual(response.data['profile']['type'], 'owner')
        # Should use username as full_name when not provided
        self.assertEqual(response.data['profile']['full_name'], 'minimaluser')