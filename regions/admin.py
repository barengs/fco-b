from django.contrib import admin
from .models import FishingArea

@admin.register(FishingArea)
class FishingAreaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'created_at')
    search_fields = ('nama',)
    ordering = ('nama',)