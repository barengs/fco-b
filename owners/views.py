"""
Owner Views (Presentation Layer)
API Views untuk manajemen pemilik kapal dan nahkoda.
Menggunakan Application Layer untuk bisnis logic.
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Owner, Captain
from .serializers import OwnerSerializer, CaptainSerializer
from .application.owner_service import OwnerApplicationService


def _is_privileged(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and (
            getattr(user, 'role', '') in ('admin', 'superadmin', 'regulator')
            or user.is_staff
            or user.is_superuser
        )
    )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Hanya administrator/regulator atau pemilik akun terkait yang dapat mengakses/mengubah profil pemilik."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if _is_privileged(request.user):
            return True
        return request.method in permissions.SAFE_METHODS or request.method in ('PUT', 'PATCH')

    def has_object_permission(self, request, view, obj):
        if _is_privileged(request.user):
            return True
        user_owner = getattr(request.user, 'owner', None)
        return user_owner is not None and obj.id == user_owner.id


class IsCaptainOwnerOrAdmin(permissions.BasePermission):
    """Hanya administrator/regulator, pemilik kapal terkait, atau nahkoda bersangkutan yang berhak mengakses."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if _is_privileged(request.user):
            return True
        if getattr(request.user, 'owner', None) is not None:
            return True
        return request.method in permissions.SAFE_METHODS or request.method in ('PUT', 'PATCH')

    def has_object_permission(self, request, view, obj):
        if _is_privileged(request.user):
            return True
        user_owner = getattr(request.user, 'owner', None)
        if user_owner is not None and obj.owner_id == user_owner.id:
            return True
        return obj.user_id == request.user.id


@extend_schema_view(
    list=extend_schema(
        tags=['Owners'],
        summary='Daftar semua pemilik kapal',
        description='Mengambil daftar seluruh pemilik kapal (perorangan atau perusahaan)'
    ),
    create=extend_schema(
        tags=['Owners'],
        summary='Buat pemilik kapal baru',
        description='Menambahkan data pemilik kapal baru'
    ),
    retrieve=extend_schema(
        tags=['Owners'],
        summary='Ambil data pemilik kapal',
        description='Mengambil data pemilik kapal tertentu berdasarkan ID'
    ),
    update=extend_schema(
        tags=['Owners'],
        summary='Perbarui pemilik kapal',
        description='Memperbarui seluruh data pemilik kapal'
    ),
    partial_update=extend_schema(
        tags=['Owners'],
        summary='Perbarui sebagian pemilik kapal',
        description='Memperbarui sebagian data pemilik kapal'
    ),
    destroy=extend_schema(
        tags=['Owners'],
        summary='Hapus pemilik kapal',
        description='Menghapus data pemilik kapal'
    ),
)
class OwnerViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola pemilik kapal (perorangan atau perusahaan)
    """
    queryset = Owner.objects.prefetch_related('ships', 'captains').all()
    serializer_class = OwnerSerializer
    permission_classes = [IsOwnerOrAdmin]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OwnerApplicationService()

    def get_queryset(self):
        qs = self.service.get_owners_queryset(
            search=self.request.query_params.get('search', None)
        )
        user = self.request.user
        if _is_privileged(user):
            return qs
        user_owner = getattr(user, 'owner', None)
        if user_owner is not None:
            return qs.filter(id=user_owner.id)
        return qs.none()


@extend_schema_view(
    list=extend_schema(
        tags=['Captains'],
        summary='Daftar semua nahkoda',
        description='Mengambil daftar semua nahkoda kapal'
    ),
    create=extend_schema(
        tags=['Captains'],
        summary='Buat nahkoda',
        description='Membuat nahkoda kapal baru'
    ),
    retrieve=extend_schema(
        tags=['Captains'],
        summary='Ambil nahkoda',
        description='Mengambil nahkoda tertentu berdasarkan ID'
    ),
    update=extend_schema(
        tags=['Captains'],
        summary='Perbarui nahkoda',
        description='Memperbarui nahkoda yang ada'
    ),
    partial_update=extend_schema(
        tags=['Captains'],
        summary='Perbarui sebagian nahkoda',
        description='Memperbarui sebagian nahkoda yang ada'
    ),
    destroy=extend_schema(
        tags=['Captains'],
        summary='Hapus nahkoda',
        description='Menghapus nahkoda'
    )
)
class CaptainViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola nahkoda kapal
    """
    queryset = Captain.objects.select_related('owner').prefetch_related('ships').all()
    serializer_class = CaptainSerializer
    permission_classes = [IsCaptainOwnerOrAdmin]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OwnerApplicationService()

    def get_queryset(self):
        user = self.request.user
        qs = self.service.get_captains_queryset(
            user=user,
            owner_id=self.request.query_params.get('owner_id'),
            search=self.request.query_params.get('search')
        )
        if _is_privileged(user) or getattr(user, 'owner', None) is not None:
            return qs
        user_captain = getattr(user, 'captain', None)
        if user_captain is not None:
            return qs.filter(id=user_captain.id)
        return qs.filter(user=user)
