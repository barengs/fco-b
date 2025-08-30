from django.contrib import admin
from .models import FishCatch, CatchDetail

@admin.register(FishCatch)
class FishCatchAdmin(admin.ModelAdmin):
    list_display = ('ship', 'catch_date', 'catch_type', 'created_at')
    list_filter = ('catch_type', 'catch_date', 'ship')
    search_fields = ('ship__name', 'description')
    date_hierarchy = 'catch_date'
    ordering = ('-catch_date',)

@admin.register(CatchDetail)
class CatchDetailAdmin(admin.ModelAdmin):
    list_display = ('fish_catch', 'fish_species', 'quantity', 'unit')
    list_filter = ('fish_species', 'unit')
    search_fields = ('fish_catch__ship__name', 'fish_species__name')