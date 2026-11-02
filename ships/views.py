"""
Ship Views (Clean Architecture Facade)
Re-exports view components from ships.presentation.views and permissions to maintain full backward compatibility.
"""

from .presentation.permissions import IsShipOwnerOrAdmin
from .presentation.views import (
    ShipViewSet,
    check_ship_registration,
    ai_ship_recommendations,
)

__all__ = [
    'IsShipOwnerOrAdmin',
    'ShipViewSet',
    'check_ship_registration',
    'ai_ship_recommendations',
]
