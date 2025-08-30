from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Custom user model that relates to the Owner model"""
    USER_ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('owner', 'Pemilik Kapal'),
        ('captain', 'Nahkoda'),
    ]
    
    owner = models.OneToOneField('Owner', on_delete=models.CASCADE, null=True, blank=True, related_name='user')
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES, default='owner', verbose_name="Peran Pengguna")
    
    def __str__(self):
        return self.username

class Owner(models.Model):
    """Model representing a ship owner (individual or company)"""
    OWNER_TYPE_CHOICES = [
        ('individual', 'Perorangan'),
        ('company', 'Perusahaan'),
    ]
    
    name = models.CharField(max_length=200)
    owner_type = models.CharField(max_length=20, choices=OWNER_TYPE_CHOICES)
    contact_info = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = "Pemilik"
        verbose_name_plural = "Pemilik"

class Captain(models.Model):
    """Model representing a ship captain (nahkoda)"""
    name = models.CharField(max_length=200, verbose_name="Nama Nahkoda")
    license_number = models.CharField(max_length=50, unique=True, verbose_name="Nomor Lisensi")
    owner = models.ForeignKey('Owner', on_delete=models.CASCADE, related_name='captains', verbose_name="Pemilik Kapal")
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='captain', verbose_name="Akun Pengguna")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Tanggal Lahir")
    contact_info = models.TextField(blank=True, null=True, verbose_name="Informasi Kontak")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Nomor Telepon")
    address = models.TextField(blank=True, null=True, verbose_name="Alamat")
    years_of_experience = models.IntegerField(null=True, blank=True, verbose_name="Tahun Pengalaman")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = "Nahkoda"
        verbose_name_plural = "Nahkoda"