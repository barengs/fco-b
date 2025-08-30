"""
Blockchain models for recording fish catch reports
"""

from django.db import models
from django.core.validators import MinValueValidator

class BlockchainBlock(models.Model):
    """Model representing a block in the blockchain"""
    index = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.TextField()
    previous_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64, unique=True)
    nonce = models.IntegerField(default=0)  # type: ignore
    
    def __str__(self):
        return f"Block {self.index} - {str(self.hash)[:10]}..."
    
    class Meta:
        verbose_name = "Blok Blockchain"
        verbose_name_plural = "Blok Blockchain"
        ordering = ['index']


class FishCatchTransaction(models.Model):
    """Model representing a fish catch transaction recorded in the blockchain"""
    # Reference to the original catch report (using string reference to avoid circular imports)
    fish_catch = models.ForeignKey('catches.FishCatch', on_delete=models.CASCADE, related_name='blockchain_transactions')
    
    # Blockchain-specific fields
    block = models.ForeignKey(BlockchainBlock, on_delete=models.CASCADE, related_name='transactions')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Data that will be stored in the blockchain
    ship_registration_number = models.CharField(max_length=100, verbose_name="Nomor Registrasi Kapal")
    fishing_area_code = models.CharField(max_length=20, verbose_name="Kode Wilayah Penangkapan")
    fish_species_code = models.CharField(max_length=100, verbose_name="Kode Jenis Ikan")
    fish_name = models.CharField(max_length=100, verbose_name="Nama Ikan")
    
    # Additional metadata
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Jumlah")
    unit = models.CharField(max_length=20, verbose_name="Satuan")
    catch_date = models.DateField(verbose_name="Tanggal Penangkapan")
    
    def __str__(self) -> str:  # type: ignore
        return f"Transaction for {self.ship_registration_number} - {self.fish_name}"
    
    class Meta:
        verbose_name = "Transaksi Blockchain Penangkapan Ikan"
        verbose_name_plural = "Transaksi Blockchain Penangkapan Ikan"


class BlockchainConfig(models.Model):
    """Model for blockchain configuration settings"""
    name = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = "Konfigurasi Blockchain"
        verbose_name_plural = "Konfigurasi Blockchain"