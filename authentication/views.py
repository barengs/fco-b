"""
Authentication Views (Presentation Layer)
Authentication views using application layer for business logic.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .application.auth_service import AuthApplicationService
from .serializers import UserRegistrationSerializer, AuthTokenSerializer


class AuthViewSet(viewsets.ViewSet):
    """
    Authentication viewset for login, registration, and logout.
    Delegates business logic to AuthApplicationService.
    """
    permission_classes = [permissions.AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthApplicationService()

    @extend_schema(
        tags=['Authentication'],
        summary='Login Pengguna',
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
                    'user_as': {'type': 'string', 'description': 'Primary user role'},
                    'roles': {'type': 'array', 'items': {'type': 'string'}, 'description': 'List of user roles'},
                    'profile': {'type': 'object', 'description': 'User profile data based on role'},
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
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        result = self.auth_service.login(username=username, password=password, request=request)

        if result is None:
            return Response({'error': 'Maaf, password dan username Anda salah'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Authentication'],
        summary='Register a new user',
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
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            result = self.auth_service.register(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                role=serializer.validated_data['role'],
                full_name=serializer.validated_data.get('full_name', ''),
                phone=serializer.validated_data.get('phone'),
                ship_code=serializer.validated_data.get('ship_code'),
            )

            if result is None:
                return Response({'error': 'Registrasi gagal'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(result, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema_view(
        logout=extend_schema(
            tags=['Authentication'],
            summary='Logout User',
            description='Logout the authenticated user by deleting their authentication token and revoking refresh tokens.',
            responses={
                200: {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string', 'description': 'Success message'}
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
    class LogoutViewSet(viewsets.ViewSet):
        """
        ViewSet for user logout
        """
        permission_classes = [permissions.IsAuthenticated]

        @action(detail=False, methods=['post'], url_path='logout')
        def logout(self, request):
            success = self.auth_service.logout(request.user)
            if success:
                return Response({'message': 'Berhasil logout'}, status=status.HTTP_200_OK)
            return Response({'error': 'Logout gagal'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
