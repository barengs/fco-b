from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from datetime import datetime, timedelta
from authentication.models import RefreshToken

User = get_user_model()


class RefreshTokenTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        self.refresh_url = '/api/auth/refresh/'
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='owner'
        )
        
        # Create auth token
        self.auth_token = Token.objects.create(user=self.user)
        
        # Create refresh token
        expires_at = datetime.now() + timedelta(days=7)
        self.refresh_token = RefreshToken.generate_token(self.user, expires_at)

    def test_login_returns_refresh_token(self):
        """Test that login endpoint returns a refresh token"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh_token', response.data)
        self.assertIn('token', response.data)
        self.assertTrue(len(response.data['refresh_token']) > 0)

    def test_refresh_token_endpoint(self):
        """Test that refresh token endpoint returns new tokens"""
        response = self.client.post(self.refresh_url, {
            'refresh_token': self.refresh_token.token
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertNotEqual(response.data['token'], self.auth_token.key)
        self.assertNotEqual(response.data['refresh_token'], self.refresh_token.token)

    def test_refresh_with_invalid_token(self):
        """Test that refresh with invalid token returns error"""
        response = self.client.post(self.refresh_url, {
            'refresh_token': 'invalid_token'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_refresh_with_expired_token(self):
        """Test that refresh with expired token returns error"""
        # Create an expired refresh token
        expired_at = datetime.now() - timedelta(days=1)
        expired_token = RefreshToken.generate_token(self.user, expired_at)
        
        response = self.client.post(self.refresh_url, {
            'refresh_token': expired_token.token
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_refresh_with_revoked_token(self):
        """Test that refresh with revoked token returns error"""
        # Revoke the refresh token
        self.refresh_token.is_revoked = True
        self.refresh_token.save()
        
        response = self.client.post(self.refresh_url, {
            'refresh_token': self.refresh_token.token
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)