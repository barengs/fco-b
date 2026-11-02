"""
Machine Learning Models for Quota Prediction (Clean Architecture Facade)
Forwarding imports to ships.infrastructure.ml to preserve full backward compatibility.
"""

from .infrastructure.ml import (
    LSTMNetwork,
    LSTMQuotaPredictor,
    NSGA3QuotaOptimizer,
    get_historical_catch_data,
    synthesize_seasonal_baseline,
    predict_and_optimize_quota,
    generate_quota_recommendation,
)

__all__ = [
    "LSTMNetwork",
    "LSTMQuotaPredictor",
    "NSGA3QuotaOptimizer",
    "get_historical_catch_data",
    "synthesize_seasonal_baseline",
    "predict_and_optimize_quota",
    "generate_quota_recommendation",
]
