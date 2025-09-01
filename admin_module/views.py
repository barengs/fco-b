from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import Permission
from .models import Role, UserRole, Menu, RoleMenu
from .serializers import RoleSerializer, UserRoleSerializer, MenuSerializer, RoleMenuSerializer, AdminUserSerializer, AdminRegistrationSerializer
from owners.models import CustomUser
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(
        tags=['Admin'],
        summary='Daftar semua peran',
        description='Mengambil daftar semua peran pengguna dalam sistem. Setiap peran dapat memiliki izin dan menu yang berbeda.'
    ),
    create=extend_schema(
        tags=['Admin'],
        summary='Buat peran baru',
        description='Membuat peran pengguna baru dalam sistem dengan nama dan deskripsi.'
    ),
    retrieve=extend_schema(
        tags=['Admin'],
        summary='Ambil peran',
        description='Mengambil peran tertentu berdasarkan ID.'
    ),
    update=extend_schema(
        tags=['Admin'],
        summary='Perbarui peran',
        description='Memperbarui peran yang ada dengan informasi baru.'
    ),
    partial_update=extend_schema(
        tags=['Admin'],
        summary='Perbarui sebagian peran',
        description='Memperbarui sebagian informasi peran yang ada.'
    ),
    destroy=extend_schema(
        tags=['Admin'],
        summary='Hapus peran',
        description='Menghapus peran dari sistem.'
    )
)
class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user roles"""
    queryset = Role.objects.all()  # type: ignore
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Tetapkan izin ke peran',
        description='Menetapkan izin tertentu ke peran pengguna.',
        request={
            'type': 'object',
            'properties': {
                'permission_id': {'type': 'integer', 'description': 'ID izin yang akan ditetapkan ke peran'}
            },
            'required': ['permission_id']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'description': 'Pesan sukses'}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Pesan kesalahan'}
                }
            },
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Pesan kesalahan'}
                }
            }
        }
    )
    @action(detail=True, methods=['post'])
    def assign_permission(self, request, pk=None):
        """Assign a permission to a role"""
        role = self.get_object()
        permission_id = request.data.get('permission_id')
        
        if not permission_id:
            return Response({'error': 'Permission ID is required'}, status=400)
        
        try:
            permission = Permission.objects.get(id=permission_id)
            role.permissions.add(permission)
            return Response({'message': 'Permission assigned successfully'})
        except Permission.DoesNotExist:  # type: ignore
            return Response({'error': 'Permission not found'}, status=404)


@extend_schema_view(
    list=extend_schema(
        tags=['Admin'],
        summary='Daftar semua hubungan pengguna-peran',
        description='Mengambil daftar semua hubungan antara pengguna dan peran dalam sistem.'
    ),
    create=extend_schema(
        tags=['Admin'],
        summary='Buat hubungan pengguna-peran',
        description='Membuat hubungan baru antara pengguna dan peran.'
    ),
    retrieve=extend_schema(
        tags=['Admin'],
        summary='Ambil hubungan pengguna-peran',
        description='Mengambil hubungan pengguna-peran tertentu berdasarkan ID.'
    ),
    update=extend_schema(
        tags=['Admin'],
        summary='Perbarui hubungan pengguna-peran',
        description='Memperbarui hubungan pengguna-peran yang ada.'
    ),
    partial_update=extend_schema(
        tags=['Admin'],
        summary='Perbarui sebagian hubungan pengguna-peran',
        description='Memperbarui sebagian informasi hubungan pengguna-peran yang ada.'
    ),
    destroy=extend_schema(
        tags=['Admin'],
        summary='Hapus hubungan pengguna-peran',
        description='Menghapus hubungan pengguna-peran dari sistem.'
    )
)
class UserRoleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user-role relationships"""
    queryset = UserRole.objects.all()  # type: ignore
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Tetapkan peran ke pengguna',
        description='Menetapkan peran tertentu ke pengguna.',
        request={
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer', 'description': 'ID pengguna yang akan diberi peran'},
                'role_id': {'type': 'integer', 'description': 'ID peran yang akan diberikan ke pengguna'}
            },
            'required': ['user_id', 'role_id']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'description': 'Pesan sukses'}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Pesan kesalahan'}
                }
            },
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Pesan kesalahan'}
                }
            }
        }
    )
    @action(detail=False, methods=['post'])
    def assign_role(self, request):
        """Assign a role to a user"""
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        
        if not user_id or not role_id:
            return Response({'error': 'User ID and Role ID are required'}, status=400)
        
        try:
            user = CustomUser.objects.get(id=user_id)  # type: ignore
            role = Role.objects.get(id=role_id)  # type: ignore
            
            user_role, created = UserRole.objects.get_or_create(user=user, role=role)  # type: ignore
            if created:
                return Response({'message': 'Role assigned successfully'})
            else:
                return Response({'message': 'Role already assigned'})
        except CustomUser.DoesNotExist:  # type: ignore
            return Response({'error': 'User not found'}, status=404)
        except Role.DoesNotExist:  # type: ignore
            return Response({'error': 'Role not found'}, status=404)


@extend_schema_view(
    list=extend_schema(
        tags=['Admin'],
        summary='Daftar semua menu',
        description='Mengambil daftar semua menu frontend yang aktif dalam sistem.'
    ),
    create=extend_schema(
        tags=['Admin'],
        summary='Buat menu',
        description='Membuat menu frontend baru.'
    ),
    retrieve=extend_schema(
        tags=['Admin'],
        summary='Ambil menu',
        description='Mengambil menu tertentu berdasarkan ID.'
    ),
    update=extend_schema(
        tags=['Admin'],
        summary='Perbarui menu',
        description='Memperbarui menu yang ada.'
    ),
    partial_update=extend_schema(
        tags=['Admin'],
        summary='Perbarui sebagian menu',
        description='Memperbarui sebagian informasi menu yang ada.'
    ),
    destroy=extend_schema(
        tags=['Admin'],
        summary='Hapus menu',
        description='Menghapus menu dari sistem.'
    )
)
class MenuViewSet(viewsets.ModelViewSet):
    """ViewSet for managing frontend menus"""
    queryset = Menu.objects.filter(is_active=True)  # type: ignore
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(
        tags=['Admin'],
        summary='Daftar semua hubungan peran-menu',
        description='Mengambil daftar semua hubungan antara peran dan menu dalam sistem.'
    ),
    create=extend_schema(
        tags=['Admin'],
        summary='Buat hubungan peran-menu',
        description='Membuat hubungan baru antara peran dan menu.'
    ),
    retrieve=extend_schema(
        tags=['Admin'],
        summary='Ambil hubungan peran-menu',
        description='Mengambil hubungan peran-menu tertentu berdasarkan ID.'
    ),
    update=extend_schema(
        tags=['Admin'],
        summary='Perbarui hubungan peran-menu',
        description='Memperbarui hubungan peran-menu yang ada.'
    ),
    partial_update=extend_schema(
        tags=['Admin'],
        summary='Perbarui sebagian hubungan peran-menu',
        description='Memperbarui sebagian informasi hubungan peran-menu yang ada.'
    ),
    destroy=extend_schema(
        tags=['Admin'],
        summary='Hapus hubungan peran-menu',
        description='Menghapus hubungan peran-menu dari sistem.'
    )
)
class RoleMenuViewSet(viewsets.ModelViewSet):
    """ViewSet for managing role-menu relationships"""
    queryset = RoleMenu.objects.all()  # type: ignore
    serializer_class = RoleMenuSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        tags=['Admin'],
        summary='Tetapkan menu ke peran',
        description='Menetapkan menu tertentu ke peran dengan izin akses yang dapat dikustomisasi.',
        request={
            'type': 'object',
            'properties': {
                'role_id': {'type': 'integer', 'description': 'ID peran yang akan diberi menu'},
                'menu_id': {'type': 'integer', 'description': 'ID menu yang akan diberikan ke peran'},
                'permissions': {
                    'type': 'object',
                    'description': 'Izin akses untuk menu (can_view, can_create, can_edit, can_delete)',
                    'properties': {
                        'can_view': {'type': 'boolean', 'description': 'Izin melihat menu'},
                        'can_create': {'type': 'boolean', 'description': 'Izin membuat data melalui menu'},
                        'can_edit': {'type': 'boolean', 'description': 'Izin mengedit data melalui menu'},
                        'can_delete': {'type': 'boolean', 'description': 'Izin menghapus data melalui menu'}
                    }
                }
            },
            'required': ['role_id', 'menu_id']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'description': 'Pesan sukses'}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Pesan kesalahan'}
                }
            },
            404: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Pesan kesalahan'}
                }
            }
        }
    )
    @action(detail=False, methods=['post'])
    def assign_menu(self, request):
        """Assign a menu to a role"""
        role_id = request.data.get('role_id')
        menu_id = request.data.get('menu_id')
        permissions = request.data.get('permissions', {})
        
        if not role_id or not menu_id:
            return Response({'error': 'Role ID and Menu ID are required'}, status=400)
        
        try:
            role = Role.objects.get(id=role_id)  # type: ignore
            menu = Menu.objects.get(id=menu_id)  # type: ignore
            
            role_menu, created = RoleMenu.objects.get_or_create(role=role, menu=menu)  # type: ignore
            
            # Update permissions
            for perm, value in permissions.items():
                if hasattr(role_menu, perm):
                    setattr(role_menu, perm, value)
            
            role_menu.save()
            
            if created:
                return Response({'message': 'Menu assigned to role successfully'})
            else:
                return Response({'message': 'Menu role permissions updated'})
        except Role.DoesNotExist:  # type: ignore
            return Response({'error': 'Role not found'}, status=404)
        except Menu.DoesNotExist:  # type: ignore
            return Response({'error': 'Menu not found'}, status=404)


@extend_schema_view(
    list=extend_schema(
        tags=['Admin'],
        summary='Daftar semua pengguna admin',
        description='Mengambil daftar semua pengguna dengan peran admin dalam sistem.'
    ),
    register=extend_schema(
        tags=['Admin'],
        summary='Daftarkan admin baru',
        description='Mendaftarkan pengguna admin baru beserta profil admin dalam satu permintaan.',
        request=AdminRegistrationSerializer,
        responses={
            201: AdminUserSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Pesan kesalahan'}
                }
            }
        }
    )
)
class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for managing admin users"""
    queryset = CustomUser.objects.filter(role='admin')  # type: ignore
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filter users who have 'admin' role
        return CustomUser.objects.filter(role='admin')
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Register a new admin user with profile"""
        serializer = AdminRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Return the created user with profile
            response_serializer = AdminUserSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
