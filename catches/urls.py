from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'fish-catches', views.FishCatchViewSet)
router.register(r'catch-details', views.CatchDetailViewSet)
router.register(r'fish-catches-with-details', views.FishCatchWithDetailsViewSet, basename='fishcatch-with-details')

urlpatterns = [
    path('', include(router.urls)),

    # PNBP Prediction endpoints
    path('pnbp/predict/', views.predict_pnbp_future, name='predict-pnbp-future'),
    path('pnbp/history/', views.get_pnbp_history, name='get-pnbp-history'),
    path('pnbp/latest-predictions/', views.get_latest_pnbp_predictions, name='get-latest-pnbp-predictions'),
]