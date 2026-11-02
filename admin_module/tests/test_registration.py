from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.response import Response
from owners.models import CustomUser
from admin_module.models import AdminProfile
from typing import cast

class AdminRegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def test_admin_registration_success(self):
        """Test successful admin registration with profile"""
        url = reverse('adminuser-register')
        data = {
            'username': 'newadmin',
            'password': 'testpassword123',
            'email': 'admin@example.com',
            'full_name': 'Admin User',
            'phone': '1234567890',
            'department': 'IT',
            'position': 'System Administrator'
        }
        
        response = self.client.post(url, data, format='json')
        # Cast to Response to help type checker
        response = cast(Response, response)
        
        # Check that the response status is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that the user was created
        self.assertTrue(CustomUser.objects.filter(username='newadmin').exists())
        
        # Check that the user has admin role
        user = CustomUser.objects.get(username='newadmin')
        self.assertEqual(user.role, 'admin')
        
        # Check that the admin profile was created
        self.assertTrue(hasattr(user, 'admin_profile'))
        profile = user.admin_profile
        self.assertEqual(profile.full_name, 'Admin User')
        self.assertEqual(profile.email, 'admin@example.com')
        self.assertEqual(profile.phone, '1234567890')
        self.assertEqual(profile.department, 'IT')
        self.assertEqual(profile.position, 'System Administrator')
        
        # Check response data
        self.assertIsNotNone(response.data)
        if response.data is not None:
            self.assertEqual(response.data['username'], 'newadmin')
            self.assertEqual(response.data['admin_profile']['full_name'], 'Admin User')
            self.assertEqual(response.data['admin_profile']['email'], 'admin@example.com')
            self.assertEqual(response.data['admin_profile']['phone'], '1234567890')
            self.assertEqual(response.data['admin_profile']['department'], 'IT')
            self.assertEqual(response.data['admin_profile']['position'], 'System Administrator')
        
    def test_admin_registration_minimum_data(self):
        """Test admin registration with minimum required data"""
        url = reverse('adminuser-register')
        data = {
            'username': 'minimaladmin',
            'password': 'testpassword123'
        }
        
        response = self.client.post(url, data, format='json')
        # Cast to Response to help type checker
        response = cast(Response, response)
        
        # Check that the response status is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that the user was created
        self.assertTrue(CustomUser.objects.filter(username='minimaladmin').exists())
        
        # Check that the user has admin role
        user = CustomUser.objects.get(username='minimaladmin')
        self.assertEqual(user.role, 'admin')
        
        # Check response data
        self.assertIsNotNone(response.data)
        if response.data is not None:
            self.assertEqual(response.data['username'], 'minimaladmin')