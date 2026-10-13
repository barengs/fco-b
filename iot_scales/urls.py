from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'devices', views.SmartScaleViewSet, basename='iot-devices')

urlpatterns = [
    # Router for device management
    path('', include(router.urls)),

    # 1. IoT Hardware Endpoint: Timbangan pintar mengirim data berat ke sini
    path('receive-weight/', views.receive_iot_weight, name='receive-iot-weight'),

    # 2. Real-time SSE Stream: Frontend mendengarkan event berat ikan secara langsung
    path('stream/', views.stream_scale_events, name='scale-stream'),

    # 3. REST Polling / Query: Frontend mengambil pembacaan berat terkini
    path('latest/', views.get_latest_scale_reading, name='scale-latest'),

    # 4. History log pembacaan timbangan
    path('readings/', views.list_scale_readings, name='scale-readings'),

    # 5. Harbor Operator Save Catch: Operator menyimpan jenis ikan & tangkapan berdasarkan berat IoT
    path('save-catch/', views.harbor_save_catch_from_scale, name='harbor-save-catch'),
]
