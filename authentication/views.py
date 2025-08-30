from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, AuthTokenSerializer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from typing import Any, Dict, Tuple
from datetime import datetime, timedelta
from .models import RefreshToken

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        summary='User Login',
        description='Authenticate user with username and password. Returns authentication token and user information.',
        request=AuthTokenSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string', 'description': 'Authentication token'},
                    'refresh_token': {'type': 'string', 'description': 'Refresh token for obtaining new authentication tokens'},
                    'user_id': {'type': 'integer', 'description': 'User ID'},
                    'username': {'type': 'string', 'description': 'Username'},
                    'user_as': {'type': 'string', 'description': 'Primary user role (admin, owner, captain, or user)', 'enum': ['admin', 'owner', 'captain', 'user']},
                    'roles': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'List of user roles'
                    },
                    'profile': {
                        'type': 'object',
                        'description': 'User profile data based on role',
                        'properties': {
                            'type': {'type': 'string', 'description': 'Profile type (admin, owner, captain, or user)'},
                            'full_name': {'type': 'string', 'description': 'Full name (admin/user profiles)'},
                            'name': {'type': 'string', 'description': 'Name (owner/captain profiles)'},
                            'email': {'type': 'string', 'format': 'email', 'description': 'Email address'},
                            'phone': {'type': 'string', 'description': 'Phone number'},
                            'department': {'type': 'string', 'description': 'Department (admin only)'},
                            'position': {'type': 'string', 'description': 'Position (admin only)'},
                            'owner_type': {'type': 'string', 'description': 'Owner type (owner only)'},
                            'address': {'type': 'string', 'description': 'Address (owner/captain only)'},
                            'license_number': {'type': 'string', 'description': 'License number (captain only)'},
                            'years_of_experience': {'type': 'integer', 'description': 'Years of experience (captain only)'}
                        }
                    }
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Error message'}
                }
            }
        }
    )
)
class CustomAuthToken(ObtainAuthToken):
    """
    Custom authentication token view that allows login with username
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=AuthTokenSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string'},
                    'refresh_token': {'type': 'string', 'description': 'Refresh token for obtaining new authentication tokens'},
                    'user_id': {'type': 'integer'},
                    'username': {'type': 'string'},
                    'user_as': {'type': 'string', 'description': 'Primary user role (admin, owner, captain, or user)', 'enum': ['admin', 'owner', 'captain', 'user']},
                    'roles': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'List of user roles'
                    },
                    'profile': {
                        'type': 'object',
                        'description': 'User profile data based on role',
                        'properties': {
                            'type': {'type': 'string', 'description': 'Profile type (admin, owner, captain, or user)'},
                            'full_name': {'type': 'string', 'description': 'Full name (admin/user profiles)'},
                            'name': {'type': 'string', 'description': 'Name (owner/captain profiles)'},
                            'email': {'type': 'string', 'format': 'email', 'description': 'Email address'},
                            'phone': {'type': 'string', 'description': 'Phone number'},
                            'department': {'type': 'string', 'description': 'Department (admin only)'},
                            'position': {'type': 'string', 'description': 'Position (admin only)'},
                            'owner_type': {'type': 'string', 'description': 'Owner type (owner only)'},
                            'address': {'type': 'string', 'description': 'Address (owner/captain only)'},
                            'license_number': {'type': 'string', 'description': 'License number (captain only)'},
                            'years_of_experience': {'type': 'integer', 'description': 'Years of experience (captain only)'}
                        }
                    }
                }
            }
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Get user from validated_data using the correct approach
        validated_data: Dict[str, Any] = serializer.validated_data  # type: ignore
        username = validated_data['username']
        password = validated_data['password']
        user = authenticate(request=request, username=username, password=password)
        
        # Additional safety check
        if not user:
            return Response({'error': 'Invalid credentials'}, status=400)
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)  # type: ignore
        
        # Create or update refresh token
        # Refresh token expires in 7 days
        expires_at = datetime.now() + timedelta(days=7)
        refresh_token_obj = RefreshToken.generate_token(user, expires_at)
        
        # Determine user type based on role
        # First check the flexible role system (admin_module)
        user_roles = []
        if hasattr(user, 'userrole_set'):
            user_roles = [user_role.role.name for user_role in user.userrole_set.all()]
        
        # Fallback to the simple role field
        is_admin = 'admin' in user_roles or user.role == 'admin'
        is_owner = 'owner' in user_roles or (hasattr(user, 'owner') and user.owner is not None)
        is_captain = 'captain' in user_roles or (hasattr(user, 'captain') and user.captain is not None)
        
        # Determine primary user role for user_as field
        if is_admin:
            user_as = 'admin'
        elif is_captain:
            user_as = 'captain'
        elif is_owner:
            user_as = 'owner'
        else:
            user_as = 'user'
        
        # Prepare response data
        response_data = {
            'token': token.key,
            'refresh_token': refresh_token_obj.token,
            'user_id': user.pk,
            'username': user.username,
            'user_as': user_as,
            'roles': user_roles if user_roles else [user.role]
        }
        
        # Add profile data based on user role
        if is_admin and hasattr(user, 'admin_profile'):
            # Admin profile
            admin_profile = user.admin_profile
            response_data['profile'] = {
                'type': 'admin',
                'full_name': admin_profile.full_name,
                'email': admin_profile.email,
                'phone': admin_profile.phone,
                'department': admin_profile.department,
                'position': admin_profile.position
            }
        elif is_owner and hasattr(user, 'owner'):
            # Owner profile
            owner = user.owner
            response_data['profile'] = {
                'type': 'owner',
                'name': owner.full_name,
                'owner_type': owner.owner_type,
                'email': owner.email,
                'phone': owner.phone,
                'address': owner.address
            }
        elif is_captain and hasattr(user, 'captain'):
            # Captain profile
            captain = user.captain
            response_data['profile'] = {
                'type': 'captain',
                'name': captain.full_name,
                'license_number': captain.license_number,
                'email': captain.email,
                'phone': captain.phone,
                'address': captain.address,
                'years_of_experience': captain.years_of_experience
            }
        else:
            # Default profile for other roles
            response_data['profile'] = {
                'type': 'user',
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username
            }
        
        return Response(response_data)


@extend_schema_view(
    post=extend_schema(
        summary='Refresh Authentication Token',
        description='Obtain a new authentication token using a refresh token.',
        request={
            'type': 'object',
            'properties': {
                'refresh_token': {'type': 'string', 'description': 'Refresh token'}
            },
            'required': ['refresh_token']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string', 'description': 'New authentication token'},
                    'refresh_token': {'type': 'string', 'description': 'Refresh token for obtaining new authentication tokens'}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Error message'}
                }
            },
            401: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Error message'}
                }
            }
        }
    )
)
class RefreshAuthToken(viewsets.ViewSet):
    """
    ViewSet for refreshing authentication tokens
    """
    permission_classes = [AllowAny]
    
    def create(self, request):
        refresh_token_key = request.data.get('refresh_token')
        
        if not refresh_token_key:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Find the refresh token
            refresh_token = RefreshToken._default_manager.get(token=refresh_token_key)  # type: ignore
            
            # Check if token is revoked or expired
            if refresh_token.is_revoked:
                return Response({'error': 'Refresh token is revoked'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if refresh_token.expires_at < datetime.now():
                return Response({'error': 'Refresh token is expired'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get or create a new authentication token
            token, created = Token.objects.get_or_create(user=refresh_token.user)  # type: ignore
            
            # Create a new refresh token
            expires_at = datetime.now() + timedelta(days=7)
            new_refresh_token_obj = RefreshToken.generate_token(refresh_token.user, expires_at)
            
            # Revoke the old refresh token
            refresh_token.is_revoked = True
            refresh_token.save()
            
            return Response({
                'token': token.key,
                'refresh_token': new_refresh_token_obj.token
            })
            
        except RefreshToken.DoesNotExist:  # type: ignore
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema_view(
    register=extend_schema(
        summary='User Registration',
        description='Register a new user with username, email, password, role, and profile information',
        request=UserRegistrationSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string', 'description': 'Authentication token'},
                    'user_id': {'type': 'integer', 'description': 'User ID'},
                    'username': {'type': 'string', 'description': 'Username'},
                    'role': {'type': 'string', 'description': 'User role'},
                    'profile': {
                        'type': 'object',
                        'description': 'User profile data based on role',
                        'properties': {
                            'type': {'type': 'string', 'description': 'Profile type (owner or captain)'},
                            'full_name': {'type': 'string', 'description': 'Full name'},
                            'contact_info': {'type': 'string', 'description': 'Contact information'},
                            'address': {'type': 'string', 'description': 'Address'},
                            'phone': {'type': 'string', 'description': 'Phone number'},
                            'email': {'type': 'string', 'format': 'email', 'description': 'Email address'},
                            'license_number': {'type': 'string', 'description': 'License number (captain only)'}
                        }
                    }
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Error message'}
                }
            }
        }
    )
)
class RegistrationViewSet(viewsets.ViewSet):
    """
    ViewSet for user registration
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)  # type: ignore
            
            # Type casting to make type checker happy
            user_pk: int = user.pk  # type: ignore
            user_username: str = user.username  # type: ignore
            
            # Prepare response data with profile information
            response_data = {
                'token': token.key,
                'user_id': user_pk,
                'username': user_username,
                'role': getattr(user, 'role', 'owner')  # type: ignore
            }
            
            # Add profile data based on role
            if getattr(user, 'role', 'owner') == 'owner' and hasattr(user, 'owner'):
                owner = user.owner
                response_data['profile'] = {
                    'type': 'owner',
                    'full_name': owner.full_name,
                    'contact_info': owner.contact_info,
                    'address': owner.address,
                    'phone': owner.phone,
                    'email': owner.email
                }
            elif getattr(user, 'role', 'owner') == 'captain' and hasattr(user, 'captain'):
                captain = user.captain
                response_data['profile'] = {
                    'type': 'captain',
                    'full_name': captain.full_name,
                    'contact_info': captain.contact_info,
                    'address': captain.address,
                    'phone': captain.phone,
                    'email': captain.email,
                    'license_number': captain.license_number
                }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)