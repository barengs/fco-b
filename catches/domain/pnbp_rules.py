"""
PNBP Domain Rules & Calculations (Domain Layer)
Enterprise rules for calculating government non-tax revenue (PNBP) on fish catches.
"""

from decimal import Decimal
from typing import Union, Optional

class PnbpRules:
    """
    Kalkulator dan aturan domain untuk penarikan PNBP Perikanan Pascaproduksi.
    Sesuai PP No. 85 Tahun 2021 tentang Jenis dan Tarif PNBP KKP.
    Formula: PNBP = Volume (kg) x Harga Patokan Ikan (HPI) x Tarif Indeks (%).
    """

    DEFAULT_TARIFF_PERCENT = Decimal('0.05')  # 5% standar
    DEFAULT_BASE_PRICE_PER_KG = Decimal('20000.0')  # Rp 20.000 / kg

    @staticmethod
    def calculate_catch_pnbp(
        quantity_kg: Union[float, Decimal, int],
        tariff_percent: Optional[Union[float, Decimal]] = None,
        base_price_per_kg: Optional[Union[float, Decimal]] = None,
    ) -> Decimal:
        qty = Decimal(str(quantity_kg or 0))
        if qty <= 0:
            return Decimal('0.00')

        rate = Decimal(str(tariff_percent)) if tariff_percent is not None else PnbpRules.DEFAULT_TARIFF_PERCENT
        if rate > 1:
            rate = rate / Decimal('100.0')

        price = Decimal(str(base_price_per_kg)) if base_price_per_kg is not None else PnbpRules.DEFAULT_BASE_PRICE_PER_KG
        production_value = qty * price
        pnbp = production_value * rate
        return round(pnbp, 2)
