from django.db import models
from django.contrib.auth.models import Permission
from owners.models import CustomUser

class Role(models.Model):
    """Model representing user roles in the system"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Nama Peran")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name="Hak Akses")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")
    
    def __str__(self) -> str:
        return str(self.name)
    
    class Meta:
        verbose_name = "Peran"
        verbose_name_plural = "Peran"

class UserRole(models.Model):
    """Model representing the relationship between users and roles"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Pengguna")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="Peran")
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Ditugaskan Pada")
    
    def __str__(self) -> str:
        # Using getattr with a fallback to handle static analysis issues
        username = getattr(self.user, 'username', 'Unknown User')
        return f"{username} - {self.role.name}"
    
    class Meta:
        unique_together = ('user', 'role')
        verbose_name = "Peran Pengguna"
        verbose_name_plural = "Peran Pengguna"

class Menu(models.Model):
    """Model representing frontend menus"""
    name = models.CharField(max_length=100, verbose_name="Nama Menu")
    url = models.CharField(max_length=200, blank=True, null=True, verbose_name="URL")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ikon")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children', verbose_name="Menu Induk")
    order = models.IntegerField(default=0, verbose_name="Urutan")  # type: ignore
    is_active = models.BooleanField(default=True, verbose_name="Aktif")  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")
    
    def __str__(self) -> str:
        return str(self.name)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Menu"
        verbose_name_plural = "Menu"

class RoleMenu(models.Model):
    """Model representing the relationship between roles and menus"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="Peran")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name="Menu")
    can_view = models.BooleanField(default=True, verbose_name="Dapat Melihat")  # type: ignore
    can_create = models.BooleanField(default=False, verbose_name="Dapat Membuat")  # type: ignore
    can_edit = models.BooleanField(default=False, verbose_name="Dapat Mengedit")  # type: ignore
    can_delete = models.BooleanField(default=False, verbose_name="Dapat Menghapus")  # type: ignore
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Ditugaskan Pada")
    
    def __str__(self) -> str:
        return f"{self.role.name} - {self.menu.name}"
    
    class Meta:
        unique_together = ('role', 'menu')
        verbose_name = "Menu Peran"
        verbose_name_plural = "Menu Peran"