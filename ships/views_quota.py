"""
Views for Quota Prediction (Clean Architecture Facade)
Re-exports view functions from ships.presentation.views.quota_endpoints for full backward compatibility.
"""

from .presentation.views.quota_endpoints import (
    predict_ship_quota,
    regulator_manual_quota_input,
)

__all__ = [
    'predict_ship_quota',
    'regulator_manual_quota_input',
]
