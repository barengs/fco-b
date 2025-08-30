from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .models import Owner, Captain
from .serializers import OwnerSerializer, CaptainSerializer, UserRegistrationSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.contrib.auth import get_user_model
from typing import Any, Dict

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        summary='Login pengguna',
        description='Login dengan username atau nomor registrasi kapal. Mengembalikan token autentikasi.'
    )
)
class CustomAuthToken(ObtainAuthToken):
    """
    Custom authentication token view that allows login with username or ship registration number
    """
    
    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Username atau nomor registrasi kapal'},
                'password': {'type': 'string', 'description': 'Password'}
            },
            'required': ['username', 'password']
        },
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
        
        # Get user from validated_data (serializer.validated_data is guaranteed to exist after is_valid())
        user = serializer.validated_data.get('user')  # type: ignore
        
        # Additional safety check
        if not user:
            return Response({'error': 'Invalid credentials'}, status=400)
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)  # type: ignore
        
        # Determine user type
        is_owner = hasattr(user, 'owner') and user.owner is not None
        is_captain = hasattr(user, 'captain') and user.captain is not None
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'is_owner': is_owner,
            'is_captain': is_captain
        })


@extend_schema_view(
    list=extend_schema(summary='Daftar semua pemilik', description='Mengambil daftar semua pemilik kapal (perorangan atau perusahaan)'),
    create=extend_schema(summary='Buat pemilik', description='Membuat pemilik kapal baru'),
    retrieve=extend_schema(summary='Ambil pemilik', description='Mengambil pemilik tertentu berdasarkan ID'),
    update=extend_schema(summary='Perbarui pemilik', description='Memperbarui pemilik yang ada'),
    partial_update=extend_schema(summary='Perbarui sebagian pemilik', description='Memperbarui sebagian pemilik yang ada'),
    destroy=extend_schema(summary='Hapus pemilik', description='Menghapus pemilik')
)
class OwnerViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola pemilik kapal (perorangan atau perusahaan)
    """
    queryset = Owner.objects.prefetch_related('ships', 'captains').all()  # type: ignore
    serializer_class = OwnerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

@extend_schema_view(
    list=extend_schema(summary='Daftar semua nahkoda', description='Mengambil daftar semua nahkoda kapal'),
    create=extend_schema(summary='Buat nahkoda', description='Membuat nahkoda kapal baru'),
    retrieve=extend_schema(summary='Ambil nahkoda', description='Mengambil nahkoda tertentu berdasarkan ID'),
    update=extend_schema(summary='Perbarui nahkoda', description='Memperbarui nahkoda yang ada'),
    partial_update=extend_schema(summary='Perbarui sebagian nahkoda', description='Memperbarui sebagian nahkoda yang ada'),
    destroy=extend_schema(summary='Hapus nahkoda', description='Menghapus nahkoda')
)
class CaptainViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola nahkoda kapal
    """
    queryset = Captain.objects.select_related('owner').prefetch_related('ships').all()  # type: ignore
    serializer_class = CaptainSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

@extend_schema_view(
    register=extend_schema(
        summary='Registrasi pengguna baru',
        description='Mendaftarkan pengguna baru dengan username, email, dan password',
        request=UserRegistrationSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string'},
                    'user_id': {'type': 'integer'},
                    'username': {'type': 'string'}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    )
)
class RegistrationViewSet(viewsets.ViewSet):
    """
    ViewSet untuk registrasi pengguna
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request) -> Response:
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Get or create token - ignoring type checker issues
            token, created = Token.objects.get_or_create(user=user)  # type: ignore
            
            # Return response with user data - ignoring type checker issues
            return Response({
                'token': token.key,
                'user_id': user.id,  # type: ignore
                'username': user.username  # type: ignore
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)