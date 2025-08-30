from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from owners.models import CustomUser, Owner, Captain
from admin_module.models import AdminProfile

User = get_user_model()


class UserAsFieldTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        
        # Create test users with different roles
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        self.owner_user = User.objects.create_user(
            username='owneruser',
            email='owner@test.com',
            password='testpass123',
            role='owner'
        )
        
        self.captain_user = User.objects.create_user(
            username='captainuser',
            email='captain@test.com',
            password='testpass123',
            role='captain'
        )
        
        # Create related profiles
        self.owner = Owner.objects.create(
            name='Test Owner',
            owner_type='individual',
            email='owner@test.com',
            phone='123456789',
            address='Test Address'
        )
        self.owner_user.owner = self.owner
        self.owner_user.save()
        
        self.captain = Captain.objects.create(
            name='Test Captain',
            license_number='CAPT123456',
            owner=self.owner,
            user=self.captain_user,
            email='captain@test.com',
            phone='987654321',
            address='Captain Address',
            years_of_experience=5
        )
        self.captain_user.captain = self.captain
        self.captain_user.save()
        
        self.admin_profile = AdminProfile.objects.create(
            user=self.admin_user,
            full_name='Admin User',
            email='admin@test.com',
            phone='111222333',
            department='IT',
            position='Administrator'
        )

    def test_admin_login_has_user_as_field(self):
        """Test that admin login includes user_as field with correct value"""
        response = self.client.post(self.login_url, {
            'username': 'adminuser',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_as', response.data)
        self.assertEqual(response.data['user_as'], 'admin')
        # Verify old fields are removed
        self.assertNotIn('is_admin', response.data)
        self.assertNotIn('is_owner', response.data)
        self.assertNotIn('is_captain', response.data)

    def test_owner_login_has_user_as_field(self):
        """Test that owner login includes user_as field with correct value"""
        response = self.client.post(self.login_url, {
            'username': 'owneruser',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_as', response.data)
        self.assertEqual(response.data['user_as'], 'owner')
        # Verify old fields are removed
        self.assertNotIn('is_admin', response.data)
        self.assertNotIn('is_owner', response.data)
        self.assertNotIn('is_captain', response.data)

    def test_captain_login_has_user_as_field(self):
        """Test that captain login includes user_as field with correct value"""
        response = self.client.post(self.login_url, {
            'username': 'captainuser',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_as', response.data)
        self.assertEqual(response.data['user_as'], 'captain')
        # Verify old fields are removed
        self.assertNotIn('is_admin', response.data)
        self.assertNotIn('is_owner', response.data)
        self.assertNotIn('is_captain', response.data)

    def test_user_with_profile_still_gets_profile_data(self):
        """Test that users still get profile data regardless of user_as field"""
        response = self.client.post(self.login_url, {
            'username': 'adminuser',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile', response.data)
        self.assertEqual(response.data['profile']['type'], 'admin')
        self.assertEqual(response.data['profile']['full_name'], 'Admin User')