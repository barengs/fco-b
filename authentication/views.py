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
                    'user_id': {'type': 'integer', 'description': 'User ID'},
                    'username': {'type': 'string', 'description': 'Username'},
                    'is_owner': {'type': 'boolean', 'description': 'Whether user is an owner'},
                    'is_captain': {'type': 'boolean', 'description': 'Whether user is a captain'}
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
                    'user_id': {'type': 'integer'},
                    'username': {'type': 'string'},
                    'is_owner': {'type': 'boolean'},
                    'is_captain': {'type': 'boolean'}
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
        
        # Determine user type
        is_owner = hasattr(user, 'owner') and user.owner is not None
        is_captain = hasattr(user, 'captain') and user.captain is not None
        
        # Type casting to make type checker happy
        user_pk: int = user.pk  # type: ignore
        user_username: str = user.username  # type: ignore
        
        return Response({
            'token': token.key,
            'user_id': user_pk,
            'username': user_username,
            'is_owner': is_owner,
            'is_captain': is_captain
        })


@extend_schema_view(
    register=extend_schema(
        summary='User Registration',
        description='Register a new user with username, email, and password',
        request=UserRegistrationSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string', 'description': 'Authentication token'},
                    'user_id': {'type': 'integer', 'description': 'User ID'},
                    'username': {'type': 'string', 'description': 'Username'}
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
            
            return Response({
                'token': token.key,
                'user_id': user_pk,
                'username': user_username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)