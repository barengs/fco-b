"""
Token Service (Authentication Infrastructure Layer)
Handles token generation and management for authentication.
"""

import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.authtoken.models import Token

from ..domain.user_role import UserRole


class TokenService:
    """
    Service for managing authentication tokens.
    Handles token generation, revocation, and lifecycle management.
    """

    def generate_token(self, user, expires_at=None) -> object:
        """
        Generate a refresh token for a user.
        """
        from ..models import RefreshToken
        if expires_at is None:
            expires_at = timezone.now() + timedelta(days=7)
        return RefreshToken.generate_token(user, expires_at)

    def revoke_all_user_tokens(self, user) -> bool:
        """
        Revoke all refresh tokens for a user.
        """
        from ..models import RefreshToken
        RefreshToken.objects.filter(user=user, is_revoked=False).update(is_revoked=True)
        return True

    def get_user_token(self, user) -> str:
        """
        Get or create authentication token for user.
        """
        from rest_framework.authtoken.models import Token
        token, created = Token.objects.get_or_create(user=user)
        return token.key
