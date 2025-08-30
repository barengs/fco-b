from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'ships', views.ShipViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('check-ship/', views.check_ship_registration, name='check_ship_registration'),
]