from django.db import models

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

class Fish(models.Model):
    """Model representing individual fish with specific characteristics"""
    
    species = models.ForeignKey(FishSpecies, on_delete=models.CASCADE, related_name='individual_fish', verbose_name="Jenis Ikan")
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nama Ikan")
    length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Panjang (cm)")
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