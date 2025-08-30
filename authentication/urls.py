from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.RegistrationViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.CustomAuthToken.as_view(), name='api_login'),
]