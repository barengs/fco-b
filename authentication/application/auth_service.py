"""
Authentication Application Service (Application Layer)
Orchestrates authentication logic: login, registration, logout, token management.
"""

from typing import Dict, Any, Optional
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils import timezone

from ..domain.user_role import UserRole
from ..domain.user_profile import UserProfile
from ..infrastructure.token_service import TokenService


class AuthApplicationService:
    """
    Application service for authentication.
    Orchestrates domain entities and infrastructure services.
    """

    def __init__(self):
        self.User = get_user_model()

    def login(self, username: str, password: str, request=None) -> Optional[Dict[str, Any]]:
        """
        Authenticate user and return login result with token and profile.
        """
        user = authenticate(request=request, username=username, password=password)
        if not user:
            return None

        return self._create_login_response(user)

    def register(self, username: str, email: str, password: str,
                 role: str, full_name: str, **profile_kwargs) -> Optional[Dict[str, Any]]:
        """
        Register a new user with role and profile.
        """
        try:
            with transaction.atomic():
                user = self.User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                )
                user.is_active = True
                user.save()

                # Create profile based on role
                profile = self._create_user_profile(user, role, full_name, **profile_kwargs)

                # Create token
                from rest_framework.authtoken.models import Token
                token = Token.objects.create(user=user)

                # Create refresh token
                from .infrastructure.token_service import TokenService
                token_service = TokenService()
                refresh_token = token_service.generate_token(user)

                return {
                    'token': token.key,
                    'refresh_token': refresh_token.token,
                    'user_id': user.pk,
                    'username': user.username,
                    'user_as': user.role,
                    'roles': [user.role],
                    'profile': self._build_profile_response(user, role, profile),
                }
        except Exception as e:
            return None

    def logout(self, user) -> bool:
        """Logout user by revoking tokens."""
        try:
            from rest_framework.authtoken.models import Token
            Token.objects.filter(user=user).delete()

            from ..infrastructure.token_service import TokenService
            TokenService.revoke_all_user_tokens(user)

            return True
        except Exception:
            return False

    def get_user_profile(self, user) -> Optional[Dict[str, Any]]:
        """Get user profile data based on role."""
        role = getattr(user, 'role', 'user')

        if role == 'superadmin':
            return self._build_superadmin_profile(user)
        elif role == 'admin':
            return self._build_admin_profile(user)
        elif role == 'regulator':
            return self._build_regulator_profile(user)
        elif role == 'captain':
            return self._build_captain_profile(user)
        elif role == 'owner':
            return self._build_owner_profile(user)
        else:
            return self._build_default_profile(user)

    def _create_user_profile(self, user, role: str, full_name: str, **kwargs):
        """Create user profile based on role."""
        if role == 'owner':
            from ..models import Owner
            return Owner.objects.create(
                user=user,
                full_name=full_name,
                owner_type=kwargs.get('owner_type', 'individual'),
                email=kwargs.get('email', ''),
                phone=kwargs.get('phone', ''),
                address=kwargs.get('address', ''),
            )
        elif role == 'captain':
            from ..models import Captain
            return Captain.objects.create(
                user=user,
                full_name=full_name,
                license_number=kwargs.get('license_number', ''),
                email=kwargs.get('email', ''),
                phone=kwargs.get('phone', ''),
                address=kwargs.get('address', ''),
                years_of_experience=kwargs.get('years_of_experience', 0),
            )
        return None

    def _build_profile_response(self, user, role: str, profile) -> dict:
        """Build profile response dict based on role."""
        if role == 'superadmin':
            return {
                'type': 'superadmin',
                'full_name': profile.full_name if profile and profile.full_name else user.username,
                'email': profile.email if admin_profile and admin_profile.email else (user.email or ''),
                'phone': profile.phone if profile else '',
                'department': profile.department if profile else 'IT Governance',
                'position': profile.position if profile and profile.position else 'Super Administrator',
            }
        elif role == 'admin':
            return {
                'type': 'admin',
                'full_name': profile.full_name if profile and profile.full_name else user.username,
                'email': profile.email if profile and profile.email else (user.email or ''),
                'phone': profile.phone if profile else '',
                'department': profile.department if profile else 'Operasional KKP',
                'position': profile.position if profile and profile.position else 'Staf Administrator',
            }
        elif role == 'regulator':
            return {
                'type': 'regulator',
                'full_name': profile.full_name if profile and profile.full_name else user.username,
                'email': profile.email if profile and profile.email else (user.email or ''),
                'phone': profile.phone if profile else '',
                'department': profile.department if profile else 'Direktorat Pengawasan',
                'position': profile.position if profile else 'Pengawas Kuota Perikanan',
            }
        elif role == 'owner' and profile:
            return {
                'id': profile.id,
                'owner_id': profile.id,
                'type': 'owner',
                'name': profile.full_name,
                'owner_type': profile.owner_type,
                'email': profile.email,
                'phone': profile.phone,
                'address': profile.address,
            }
        elif role == 'captain' and profile:
            return {
                'type': 'captain',
                'name': profile.full_name,
                'license_number': profile.license_number,
                'email': profile.email,
                'phone': profile.phone,
                'address': profile.address,
                'years_of_experience': profile.years_of_experience
            }
        else:
            return {
                'type': 'user',
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            }

    def _build_superadmin_profile(self, user) -> dict:
        profile = getattr(user, 'admin_profile', None)
        return {
            'type': 'superadmin',
            'full_name': profile.full_name if profile and profile.full_name else user.username,
            'email': profile.email if profile and profile.email else (user.email or ''),
            'phone': profile.phone if profile else '',
            'department': profile.department if profile else 'IT Governance',
            'position': profile.position if profile and profile.position else 'Super Administrator',
        }

    def _build_admin_profile(self, user) -> dict:
        profile = getattr(user, 'admin_profile', None)
        return {
            'type': 'admin',
            'full_name': profile.full_name if profile and profile.full_name else user.username,
            'email': profile.email if profile and profile.email else (user.email or ''),
            'phone': profile.phone if profile else '',
            'department': profile.department if profile else 'Operasional KKP',
            'position': profile.position if profile and profile.position else 'Staf Administrator',
        }

    def _build_regulator_profile(self, user) -> dict:
        profile = getattr(user, 'admin_profile', None)
        return {
            'type': 'regulator',
            'full_name': profile.full_name if profile and profile.full_name else user.username,
            'email': profile.email if profile and profile.email else (user.email or ''),
            'phone': profile.phone if profile else '',
            'department': profile.department if profile else 'Direktorat Pengawasan',
            'position': profile.position if profile else 'Pengawas Kuota Perikanan',
        }

    def _build_captain_profile(self, user) -> dict:
        profile = getattr(user, 'captain', None)
        return {
            'type': 'captain',
            'name': profile.full_name if profile else user.username,
            'license_number': profile.license_number if profile else '',
            'email': profile.email if profile else '',
            'phone': profile.phone if profile else '',
            'address': profile.address if profile else '',
            'years_of_experience': profile.years_of_experience if profile else 0,
        }

    def _build_owner_profile(self, user) -> dict:
        profile = getattr(user, 'owner', None)
        return {
            'type': 'owner',
            'name': profile.full_name if profile else user.username,
            'owner_type': profile.owner_type if profile else '',
            'email': profile.email if profile else '',
            'phone': profile.phone if profile else '',
            'address': profile.address if profile else '',
        }

    def _build_default_profile(self, user) -> dict:
        return {
            'type': 'user',
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
        }
