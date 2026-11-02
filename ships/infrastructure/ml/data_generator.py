"""
Historical Catch Data Provider & Synthesizer
Retrieves catch logs from the database or synthesizes cold-start baselines based on GT and seasonal cycles.
"""

import math
from datetime import datetime, timedelta
from django.apps import apps
from django.db.models import Sum
from django.db.models.functions import TruncMonth

def get_historical_catch_data(ship_registration_number, months_back=24):
    """
    Retrieve historical catch data for a specific ship.
    """
    try:
        Ship = apps.get_model('ships', 'Ship')
        FishCatch = apps.get_model('catches', 'FishCatch')

        ship = Ship._default_manager.get(registration_number=ship_registration_number)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=months_back * 30)

        catch_reports = FishCatch.objects.filter(
            ship=ship,
            catch_date__gte=start_date,
            catch_date__lte=end_date
        ).order_by('catch_date')

        monthly_catches = catch_reports.annotate(
            month=TruncMonth('catch_date')
        ).values('month').annotate(
            total_catch=Sum('catch_details__quantity')
        ).order_by('month')

        catch_data = [
            float(item['total_catch'])
            for item in monthly_catches
            if item['total_catch'] is not None
        ]

        return catch_data, ship
    except Exception:
        return [], None

def synthesize_seasonal_baseline(ship, historical_data=None):
    """
    Synthesizes a realistic seasonal baseline reflecting Indonesian maritime cycles
    when historical catch data is insufficient (< 7 months).
    """
    gt = float(getattr(ship, 'gross_tonnage', 0) or 50.0)
    existing_mean = (sum(historical_data) / len(historical_data)) if historical_data else (gt * 20.0)
    base_monthly = max(existing_mean, 800.0)

    # Seasonal factors for 24 months (peak in Apr-May & Sep-Oct)
    seasonal_factors = [0.85, 0.90, 1.10, 1.25, 1.20, 0.95, 0.80, 0.75, 1.15, 1.30, 1.10, 0.90]
    synthesized = []
    for i in range(24):
        factor = seasonal_factors[i % 12]
        noise = 1.0 + 0.05 * math.sin(i * 1.5)
        synthesized.append(round(base_monthly * factor * noise, 2))

    if historical_data:
        synthesized = synthesized[:-len(historical_data)] + list(historical_data)

    return synthesized
