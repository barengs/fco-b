from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import Permission
from .models import Role, UserRole, Menu, RoleMenu
from .serializers import RoleSerializer, UserRoleSerializer, MenuSerializer, RoleMenuSerializer
from owners.models import CustomUser


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user roles"""
    queryset = Role.objects.all()  # type: ignore
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
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


class UserRoleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user-role relationships"""
    queryset = UserRole.objects.all()  # type: ignore
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
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


class MenuViewSet(viewsets.ModelViewSet):
    """ViewSet for managing frontend menus"""
    queryset = Menu.objects.filter(is_active=True)  # type: ignore
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated]


class RoleMenuViewSet(viewsets.ModelViewSet):
    """ViewSet for managing role-menu relationships"""
    queryset = RoleMenu.objects.all()  # type: ignore
    serializer_class = RoleMenuSerializer
    permission_classes = [permissions.IsAuthenticated]
    
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