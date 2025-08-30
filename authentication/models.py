from django.db import models
from django.contrib.auth import get_user_model
import secrets
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()


class RefreshToken(models.Model):
    """Model for storing refresh tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)  # type: ignore
    
    def __str__(self) -> str:
        user_username = getattr(self.user, 'username', 'Unknown User')
        return f"RefreshToken for {user_username}"
    
    @classmethod
    def generate_token(cls, user: 'AbstractUser', expires_at) -> 'RefreshToken':
        """Generate a new refresh token for a user"""
        token = secrets.token_urlsafe(32)
        # Type checking fix for Django models
        return cls._default_manager.create(  # type: ignore
            user=user,
            token=token,
            expires_at=expires_at
        )
    
    class Meta:
        verbose_name = "Refresh Token"
        verbose_name_plural = "Refresh Tokens"