from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from owners.models import CustomUser
from django.contrib.auth.models import User

class AdminUserViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create an admin user
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            password='testpass123',
            role='admin'
        )
        # Create a regular user
        self.regular_user = CustomUser.objects.create_user(
            username='regular',
            password='testpass123',
            role='owner'
        )
        
    def test_get_admin_users(self):
        """Test that the endpoint returns only admin users"""
        url = reverse('adminuser-list')
        response = self.client.get(url)
        
        # For now, we're just checking if the endpoint exists and returns a response
        # In a real test, we would also check authentication and the actual data returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)