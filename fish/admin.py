from django.contrib import admin
from .models import FishSpecies, Fish

@admin.register(FishSpecies)
class FishSpeciesAdmin(admin.ModelAdmin):
    list_display = ('name', 'scientific_name')
    search_fields = ('name', 'scientific_name')
    ordering = ('name',)

@admin.register(Fish)
class FishAdmin(admin.ModelAdmin):
    list_display = ('species', 'name')
    list_filter = ('species',)
    search_fields = ('name', 'species__name')
    ordering = ('-created_at',)