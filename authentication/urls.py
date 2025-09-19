from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.RegistrationViewSet, basename='auth')
router.register(r'', views.LogoutViewSet, basename='logout')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.CustomAuthToken.as_view(), name='api_login'),
    path('refresh/', views.RefreshAuthToken.as_view({'post': 'create'}), name='api_refresh'),
]