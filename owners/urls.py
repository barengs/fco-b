from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = DefaultRouter()
router.register(r'owners', views.OwnerViewSet)
router.register(r'captains', views.CaptainViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.CustomAuthToken.as_view(), name='api_login'),
]