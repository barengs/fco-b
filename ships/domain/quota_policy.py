"""
Ship Quota Policy (Domain Layer)
Pure business rules for vessel fishing quota compliance and thresholds.
"""

from decimal import Decimal
from typing import Dict, Any, Union

class QuotaPolicy:
    """Enterprise policy rules for fishing quota thresholds and compliance status."""

    CRITICAL_THRESHOLD_PERCENT = 15.0
    WARNING_THRESHOLD_PERCENT = 35.0

    @staticmethod
    def calculate_remaining_quota(total_quota: Union[float, Decimal], used_quota: Union[float, Decimal]) -> float:
        total = float(total_quota or 0.0)
        used = float(used_quota or 0.0)
        return max(0.0, total - used)

    @staticmethod
    def calculate_remaining_percentage(total_quota: Union[float, Decimal], used_quota: Union[float, Decimal]) -> float:
        total = float(total_quota or 0.0)
        if total <= 0:
            return 0.0
        rem = QuotaPolicy.calculate_remaining_quota(total, used_quota)
        return round((rem / total) * 100.0, 2)

    @staticmethod
    def determine_status(total_quota: Union[float, Decimal], used_quota: Union[float, Decimal]) -> str:
        pct = QuotaPolicy.calculate_remaining_percentage(total_quota, used_quota)
        if pct < QuotaPolicy.CRITICAL_THRESHOLD_PERCENT:
            return "Kritis"
        elif pct < QuotaPolicy.WARNING_THRESHOLD_PERCENT:
            return "Waspada"
        return "Aman"

    @classmethod
    def evaluate_compliance(cls, total_quota: Union[float, Decimal], used_quota: Union[float, Decimal]) -> Dict[str, Any]:
        total = float(total_quota or 0.0)
        used = float(used_quota or 0.0)
        rem = cls.calculate_remaining_quota(total, used)
        pct = cls.calculate_remaining_percentage(total, used)
        status = cls.determine_status(total, used)
        return {
            "total_quota_kg": total,
            "used_quota_kg": used,
            "remaining_quota_kg": rem,
            "remaining_percentage": pct,
            "status": status,
            "is_critical": status == "Kritis",
            "is_warning": status == "Waspada",
            "is_safe": status == "Aman",
        }
