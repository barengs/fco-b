from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'fish-catches', views.FishCatchViewSet)
router.register(r'catch-details', views.CatchDetailViewSet)
router.register(r'fish-catches-with-details', views.FishCatchWithDetailsViewSet, basename='fishcatch-with-details')

urlpatterns = [
    # Support import_csv and download_template on both fish-catches and fish-catches-with-details
    path('fish-catches/import_csv/', views.FishCatchWithDetailsViewSet.as_view({'post': 'import_csv'}), name='fishcatch-import-csv-alias'),
    path('fish-catches/download_template/', views.FishCatchWithDetailsViewSet.as_view({'get': 'download_template'}), name='fishcatch-download-template-alias'),

    path('', include(router.urls)),

    # PNBP Prediction endpoints
    path('pnbp/predict/', views.predict_pnbp_future, name='predict-pnbp-future'),
    path('pnbp/history/', views.get_pnbp_history, name='get-pnbp-history'),
    path('pnbp/latest-predictions/', views.get_latest_pnbp_predictions, name='get-latest-pnbp-predictions'),

    # Unified Chart Data endpoint
    path('charts/unified/', views.get_unified_chart_data, name='get-unified-chart-data'),
]