from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'fish-catches', views.FishCatchViewSet)
router.register(r'catch-details', views.CatchDetailViewSet)
router.register(r'fish-catches-with-details', views.FishCatchWithDetailsViewSet, basename='fishcatch-with-details')

urlpatterns = [
    path('', include(router.urls)),
]