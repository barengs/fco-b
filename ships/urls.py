from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_quota import predict_ship_quota

router = DefaultRouter()
router.register(r'ships', views.ShipViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('check-ship/', views.check_ship_registration, name='check_ship_registration'),
    path('ai-recommendations/', views.ai_ship_recommendations, name='ai_ship_recommendations'),
    path('predict-quota/', predict_ship_quota, name='predict_ship_quota'),
]