from django.db import models
from django.core.validators import MinValueValidator

class FishSpecies(models.Model):
    """Model representing fish species"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nama Ikan")
    scientific_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nama Ilmiah")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.name) if self.name else "Unnamed Fish Species"
    
    class Meta:
        verbose_name = "Jenis Ikan"
        verbose_name_plural = "Jenis Ikan"

class FishPriceReference(models.Model):
    """Model for reference prices of fish species for PNBP calculation"""
    fish_species = models.OneToOneField(FishSpecies, on_delete=models.CASCADE, related_name='price_reference', verbose_name="Jenis Ikan")
    price_per_kg = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Harga Acuan per kg (Rp)")
    effective_date = models.DateField(auto_now_add=True, verbose_name="Tanggal Efektif")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    def __str__(self):
        return f"Harga {self.fish_species.name}: Rp {self.price_per_kg}/kg"

    class Meta:
        verbose_name = "Harga Acuan Ikan"
        verbose_name_plural = "Harga Acuan Ikan"
        unique_together = ['fish_species', 'effective_date']  # Allow multiple prices over time

class Fish(models.Model):
    """Model representing individual fish with specific characteristics"""

    species = models.ForeignKey(FishSpecies, on_delete=models.CASCADE, related_name='individual_fish', verbose_name="Jenis Ikan")
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nama Ikan")
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Berat (kg)")
    notes = models.TextField(blank=True, null=True, verbose_name="Catatan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            species_name = self.species.name if self.species else 'Unknown Species'
            return f"{self.name} ({species_name})"
        else:
            species_name = self.species.name if self.species else 'Unknown Species'
            return f"Ikan {species_name}"

    class Meta:
        verbose_name = "Ikan"
        verbose_name_plural = "Ikan"