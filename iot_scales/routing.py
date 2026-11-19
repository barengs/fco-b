"""
WebSocket Routing for IoT Scales
Maps WebSocket URLs to consumers.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/scales/(?P<device_id>[\w-]+)/?$', consumers.SmartScaleConsumer.as_asgi()),
    re_path(r'^ws/scales/?$', consumers.SmartScaleConsumer.as_asgi()),
]
