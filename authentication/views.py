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


"""
Authentication Views (Presentation Layer)
Authentication views using application layer for business logic.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .application.auth_service import AuthApplicationService
from .serializers import (
    UserRegistrationSerializer,
    AuthTokenSerializer,
    RefreshTokenInputSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    PasswordResetConfirmSerializer,
)


class AuthViewSet(viewsets.ViewSet):
    """
    Authentication viewset for login, registration, refresh token, logout, and password reset.
    Delegates business logic to AuthApplicationService.
    """
    permission_classes = [permissions.AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthApplicationService()

    @extend_schema(
        tags=['Authentication'],
        summary='Login Pengguna',
        description='Authenticate user with username or ship registration number and password. Returns authentication token and user profile.',
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

    @extend_schema(
        tags=['Authentication'],
        summary='Refresh Authentication Token',
        description='Memperbarui token otentikasi menggunakan refresh token yang masih valid.',
        request=RefreshTokenInputSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string', 'description': 'Token otentikasi baru'},
                    'refresh_token': {'type': 'string', 'description': 'Refresh token baru'}
                }
            },
            400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
            401: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        }
    )
    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh(self, request):
        serializer = RefreshTokenInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        result = self.auth_service.refresh_token(serializer.validated_data['refresh_token'])
        if result.get('success'):
            return Response(result['data'], status=status.HTTP_200_OK)
        return Response({'error': result.get('error')}, status=result.get('status_code', status.HTTP_400_BAD_REQUEST))

    @extend_schema(
        tags=['Authentication'],
        summary='Logout Pengguna',
        description='Keluar dari sesi dengan menghapus token autentikasi aktif dan mencabut refresh token.',
        responses={
            200: {'type': 'object', 'properties': {'message': {'type': 'string'}}},
            500: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        }
    )
    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        success = self.auth_service.logout(request.user)
        if success:
            return Response({'message': 'Berhasil logout'}, status=status.HTTP_200_OK)
        return Response({'error': 'Logout gagal'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=['Authentication'],
        summary='Minta Kode OTP Reset Kata Sandi',
        description='''Mengirim kode OTP verifikasi 6 digit ke email akun atau nomor registrasi kapal.
        Tahap 1 dari wizard Reset Password.''',
        request=PasswordResetRequestSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'identifier': {'type': 'string'},
                    'masked_email': {'type': 'string'},
                    'otp_preview': {'type': 'string', 'description': 'Kode OTP untuk pengujian langsung'}
                }
            },
            400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        }
    )
    @action(detail=False, methods=['post'], url_path='reset-password/request')
    def reset_password_request(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        result = self.auth_service.request_password_reset(serializer.validated_data['identifier'])
        if result.get('success'):
            return Response(result, status=status.HTTP_200_OK)
        return Response({'error': result.get('error')}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['Authentication'],
        summary='Verifikasi Kode OTP Reset Sandi',
        description='''Memverifikasi keabsahan kode OTP 6 digit yang dimasukkan pengguna.
        Tahap 2 dari wizard Reset Password.''',
        request=PasswordResetVerifySerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'reset_token': {'type': 'string', 'description': 'Token sesi reset untuk konfirmasi sandi'}
                }
            },
            400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        }
    )
    @action(detail=False, methods=['post'], url_path='reset-password/verify')
    def reset_password_verify(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        result = self.auth_service.verify_password_reset_otp(
            identifier=serializer.validated_data['identifier'],
            otp=serializer.validated_data['otp']
        )
        if result.get('success'):
            return Response(result, status=status.HTTP_200_OK)
        return Response({'error': result.get('error')}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['Authentication'],
        summary='Konfirmasi & Simpan Kata Sandi Baru',
        description='''Menetapkan kata sandi baru (minimal 8 karakter) setelah kode OTP terverifikasi.
        Tahap 3 dari wizard Reset Password.''',
        request=PasswordResetConfirmSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'}
                }
            },
            400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        }
    )
    @action(detail=False, methods=['post'], url_path='reset-password/confirm')
    def reset_password_confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        result = self.auth_service.confirm_password_reset(
            identifier=serializer.validated_data.get('identifier', ''),
            new_password=serializer.validated_data['new_password'],
            confirm_password=serializer.validated_data['confirm_password'],
            otp=serializer.validated_data.get('otp'),
            reset_token=serializer.validated_data.get('reset_token'),
        )
        if result.get('success'):
            return Response(result, status=status.HTTP_200_OK)
        return Response({'error': result.get('error')}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['Authentication'],
        summary='Reset Kata Sandi (Alur Langsung)',
        description='Reset kata sandi langsung dengan identifier, OTP/token, dan password baru dalam satu request.',
        request=PasswordResetConfirmSerializer,
        responses={
            200: {'type': 'object', 'properties': {'success': {'type': 'boolean'}, 'message': {'type': 'string'}}},
            400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        }
    )
    @action(detail=False, methods=['post'], url_path='reset-password')
    def reset_password(self, request):
        return self.reset_password_confirm(request)
