import uuid
import secrets
from django.db import models
from django.core.validators import MinValueValidator


class SmartScale(models.Model):
    """
    Model representing an IoT Smart Scale device deployed at a harbor/port.
    """
    device_id = models.CharField(max_length=50, unique=True, verbose_name="ID Perangkat / Timbangan")
    name = models.CharField(max_length=100, verbose_name="Nama Timbangan")
    port_name = models.CharField(max_length=100, verbose_name="Nama Pelabuhan / Lokasi")
    api_key = models.CharField(max_length=64, blank=True, null=True, verbose_name="API Key / Token Perangkat")
    is_active = models.BooleanField(default=True, verbose_name="Status Aktif")
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Terakhir Terlihat")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = f"iot_{secrets.token_hex(16)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.device_id}) - {self.port_name}"

    class Meta:
        verbose_name = "Timbangan Pintar IoT"
        verbose_name_plural = "Timbangan Pintar IoT"


class ScaleReading(models.Model):
    """
    Model storing real-time weight measurements received from IoT smart scales.
    Operator at the harbor views these readings on the frontend in real time,
    fills in the fish species and ship details, and saves it into the database.
    """
    STATUS_CHOICES = [
        ('pending', 'Menunggu Diproses'),
        ('saved', 'Tersimpan ke Tangkapan'),
        ('discarded', 'Dibatalkan / Dilewati'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scale = models.ForeignKey(
        SmartScale,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='readings',
        verbose_name="Timbangan"
    )
    device_id = models.CharField(max_length=50, db_index=True, verbose_name="ID Perangkat")
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Berat (kg)"
    )
    unit = models.CharField(max_length=20, default='kg', verbose_name="Satuan")
    tare = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Tara (kg)"
    )
    is_stable = models.BooleanField(
        default=True,
        verbose_name="Stabil (Valid)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        verbose_name="Status Pembacaan"
    )
    session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="ID Sesi / Batch Timbang"
    )

    # Reference to the resulting catch after user saves it on frontend
    fish_catch = models.ForeignKey(
        'catches.FishCatch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scale_readings',
        verbose_name="Laporan Tangkapan Terkait"
    )
    catch_detail = models.ForeignKey(
        'catches.CatchDetail',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scale_readings',
        verbose_name="Detail Tangkapan Terkait"
    )

    operator_notes = models.TextField(blank=True, null=True, verbose_name="Catatan Operator")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Waktu Ditimbang")

    def __str__(self):
        return f"[{self.device_id}] {self.weight} {self.unit} ({self.status}) - {self.created_at:%Y-%m-%d %H:%M:%S}"

    class Meta:
        verbose_name = "Data Timbangan Ikan"
        verbose_name_plural = "Data Timbangan Ikan"
        ordering = ['-created_at']
