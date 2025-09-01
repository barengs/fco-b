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

class CatchDetail(models.Model):
    """Model representing details of a fish catch (specific species and quantities)"""
    fish_catch = models.ForeignKey(FishCatch, on_delete=models.CASCADE, related_name='catch_details', verbose_name="Laporan Penangkapan")
    fish_species = models.ForeignKey(FishSpecies, on_delete=models.CASCADE, verbose_name="Jenis Ikan")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Jumlah")
    unit = models.CharField(max_length=20, default='kg', verbose_name="Satuan")  # kg, tons, etc.
    value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Nilai")  # monetary value
    notes = models.TextField(blank=True, null=True, verbose_name="Catatan")
    
    def __str__(self):
        return f"{self.fish_species.name}: {self.quantity} {self.unit}"
    
    class Meta:
        verbose_name = "Detail Penangkapan"
        verbose_name_plural = "Detail Penangkapan"