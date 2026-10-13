import uuid
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catches', '0004_tariff_catchdetail_pnbp_catchdetail_pnkp_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmartScale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(max_length=50, unique=True, verbose_name='ID Perangkat / Timbangan')),
                ('name', models.CharField(max_length=100, verbose_name='Nama Timbangan')),
                ('port_name', models.CharField(max_length=100, verbose_name='Nama Pelabuhan / Lokasi')),
                ('api_key', models.CharField(blank=True, max_length=64, null=True, verbose_name='API Key / Token Perangkat')),
                ('is_active', models.BooleanField(default=True, verbose_name='Status Aktif')),
                ('last_seen', models.DateTimeField(blank=True, null=True, verbose_name='Terakhir Terlihat')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Dibuat Pada')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Diperbarui Pada')),
            ],
            options={
                'verbose_name': 'Timbangan Pintar IoT',
                'verbose_name_plural': 'Timbangan Pintar IoT',
            },
        ),
        migrations.CreateModel(
            name='ScaleReading',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('device_id', models.CharField(db_index=True, max_length=50, verbose_name='ID Perangkat')),
                ('weight', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Berat (kg)')),
                ('unit', models.CharField(default='kg', max_length=20, verbose_name='Satuan')),
                ('tare', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Tara (kg)')),
                ('is_stable', models.BooleanField(default=True, verbose_name='Stabil (Valid)')),
                ('status', models.CharField(choices=[('pending', 'Menunggu Diproses'), ('saved', 'Tersimpan ke Tangkapan'), ('discarded', 'Dibatalkan / Dilewati')], db_index=True, default='pending', max_length=20, verbose_name='Status Pembacaan')),
                ('session_id', models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='ID Sesi / Batch Timbang')),
                ('operator_notes', models.TextField(blank=True, null=True, verbose_name='Catatan Operator')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Waktu Ditimbang')),
                ('catch_detail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='scale_readings', to='catches.catchdetail', verbose_name='Detail Tangkapan Terkait')),
                ('fish_catch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='scale_readings', to='catches.fishcatch', verbose_name='Laporan Tangkapan Terkait')),
                ('scale', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='readings', to='iot_scales.smartscale', verbose_name='Timbangan')),
            ],
            options={
                'verbose_name': 'Data Timbangan Ikan',
                'verbose_name_plural': 'Data Timbangan Ikan',
                'ordering': ['-created_at'],
            },
        ),
    ]
