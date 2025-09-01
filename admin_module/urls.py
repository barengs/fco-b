from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, UserRoleViewSet, MenuViewSet, RoleMenuViewSet, AdminUserViewSet

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'user-roles', UserRoleViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'role-menus', RoleMenuViewSet)
router.register(r'admin-users', AdminUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]