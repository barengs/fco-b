from django.db import models

class FishingArea(models.Model):
    """Model representing fishing areas/regions"""
    nama = models.CharField(max_length=200, verbose_name="Nama Wilayah")
    code = models.CharField(max_length=20, unique=True, verbose_name="Kode Wilayah")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
      # JSON or text representation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = "Wilayah Penangkapan"
        verbose_name_plural = "Wilayah Penangkapan"