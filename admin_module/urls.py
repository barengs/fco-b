from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, UserRoleViewSet, MenuViewSet, RoleMenuViewSet

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'user-roles', UserRoleViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'role-menus', RoleMenuViewSet)

urlpatterns = [
    path('', include(router.urls)),
]