from django.contrib import admin
from .models import SmartScale, ScaleReading


@admin.register(SmartScale)
class SmartScaleAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'name', 'port_name', 'is_active', 'last_seen', 'api_key', 'created_at')
    list_filter = ('is_active', 'port_name')
    search_fields = ('device_id', 'name', 'port_name')


@admin.register(ScaleReading)
class ScaleReadingAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'weight', 'unit', 'is_stable', 'status', 'fish_catch', 'created_at')
    list_filter = ('status', 'is_stable', 'unit', 'created_at')
    search_fields = ('device_id', 'session_id')
    readonly_fields = ('id', 'created_at')
