from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'fish-species', views.FishSpeciesViewSet)
router.register(r'fish', views.FishViewSet)

urlpatterns = [
    path('', include(router.urls)),
]