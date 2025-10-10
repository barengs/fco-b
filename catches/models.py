from django.db.models.fields import DecimalField


from django.db import models
from django.core.validators import MinValueValidator
from ships.models import Ship
from fish.models import FishSpecies

class FishCatch(models.Model):
    """Model representing a fish catch report"""
    CATCH_TYPE_CHOICES = [
        ('pelagic', 'Pelagis'),
        ('demersal', 'Demersal'),
        ('reef', 'Terumbu Karang'),
    ]
    
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name='catch_reports', verbose_name="Kapal")
    catch_date = models.DateField(verbose_name="Tanggal Penangkapan")
    catch_type = models.CharField(max_length=20, choices=CATCH_TYPE_CHOICES, verbose_name="Jenis Penangkapan")
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitude Lokasi")
    location_longitude: DecimalField = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitude Lokasi")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Laporan penangkapan untuk {self.ship.name} pada {self.catch_date}"
    
    class Meta:
        verbose_name = "Penangkapan Ikan"
        verbose_name_plural = "Penangkapan Ikan"

class Tariff(models.Model):
    """Model for PNBP tariff configuration"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nama Tarif")
    gt_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=60, validators=[MinValueValidator(0)], verbose_name="Batas GT")
    rate_small = models.DecimalField(max_digits=5, decimal_places=4, default=0.05, validators=[MinValueValidator(0)], verbose_name="Tarif GT Kecil (%)")
    rate_large = models.DecimalField(max_digits=5, decimal_places=4, default=0.10, validators=[MinValueValidator(0)], verbose_name="Tarif GT Besar (%)")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    effective_date = models.DateField(auto_now_add=True, verbose_name="Tanggal Efektif")

    def __str__(self):
        return f"Tarif {self.name}: GT <= {self.gt_threshold} = {self.rate_small*100}%, > {self.gt_threshold} = {self.rate_large*100}%"

    class Meta:
        verbose_name = "Tarif PNBP"
        verbose_name_plural = "Tarif PNBP"

class CatchDetail(models.Model):
    """Model representing details of a fish catch (specific species and quantities)"""
    fish_catch = models.ForeignKey(FishCatch, on_delete=models.CASCADE, related_name='catch_details', verbose_name="Laporan Penangkapan")
    fish_species = models.ForeignKey(FishSpecies, on_delete=models.CASCADE, verbose_name="Jenis Ikan")
    wpp = models.ForeignKey('regions.FishingArea', on_delete=models.CASCADE, verbose_name="WPP",  null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Jumlah")
    unit = models.CharField(max_length=20, default='kg', verbose_name="Satuan")  # kg, tons, etc.
    value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Nilai")  # monetary value
    # PNBP calculation fields
    tarif_index = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True, verbose_name="Tarif Index")
    pnkp = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name="PNKP (Nilai Produksi Ikan)")
    pnbp = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name="PNBP")
    notes = models.TextField(blank=True, null=True, verbose_name="Catatan")

    def calculate_pnbp(self):
        """Calculate PNBP based on ship's GT, quantity, and reference price"""
        if not self.fish_catch.ship.gross_tonnage or not self.quantity or self.quantity <= 0:
            return None

        # Get active tariff
        tariff = Tariff.objects.filter(is_active=True).first()
        if not tariff:
            # Default tariff
            tariff = Tariff(gt_threshold=60, rate_small=0.05, rate_large=0.10)

        # Get reference price
        try:
            price_ref = self.fish_species.price_reference.filter(is_active=True).latest('effective_date')
            harga = price_ref.price_per_kg
        except:
            return None  # No price reference

        gt = self.fish_catch.ship.gross_tonnage
        volume = float(self.quantity)  # assuming kg

        tarif_index = tariff.rate_small if gt <= tariff.gt_threshold else tariff.rate_large
        pnkp = volume * float(harga)
        pnbp = pnkp * float(tarif_index)

        self.tarif_index = tarif_index
        self.pnkp = pnkp
        self.pnbp = pnbp

        return {
            'tarif_index': tarif_index,
            'pnkp': pnkp,
            'pnbp': pnbp
        }

    def save(self, *args, **kwargs):
        if self.fish_catch.ship.gross_tonnage and self.quantity > 0:
            self.calculate_pnbp()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fish_species.name}: {self.quantity} {self.unit}"

    class Meta:
        verbose_name = "Detail Penangkapan"
        verbose_name_plural = "Detail Penangkapan"