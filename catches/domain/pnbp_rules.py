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
    def determine_tariff_rate(
        gross_tonnage: Union[float, Decimal, int],
        threshold: Union[float, Decimal, int] = 60,
        rate_small: Union[float, Decimal] = Decimal('0.05'),
        rate_large: Union[float, Decimal] = Decimal('0.10'),
    ) -> Decimal:
        """
        Menentukan tarif indeks PNBP berdasarkan kapasitas GT kapal sesuai PP 85/2021.
        GT <= threshold: tarif kecil (default 5%)
        GT > threshold: tarif besar (default 10%)
        """
        gt = Decimal(str(gross_tonnage or 0))
        limit = Decimal(str(threshold or 60))
        return Decimal(str(rate_small)) if gt <= limit else Decimal(str(rate_large))

    @staticmethod
    def calculate_production_value(
        quantity_kg: Union[float, Decimal, int],
        base_price_per_kg: Optional[Union[float, Decimal]] = None,
    ) -> Decimal:
        """
        Menghitung Pendapatan Nilai Kasar Produksi (PNKP = Volume x HPI).
        """
        qty = Decimal(str(quantity_kg or 0))
        if qty <= 0:
            return Decimal('0.00')
        price = Decimal(str(base_price_per_kg)) if base_price_per_kg is not None else PnbpRules.DEFAULT_BASE_PRICE_PER_KG
        return round(qty * price, 2)

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
