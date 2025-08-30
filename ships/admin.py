from django.contrib import admin
from .models import Ship

@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'owner', 'captain', 'active', 'year_built')
    list_filter = ('active', 'year_built', 'owner', 'captain')
    search_fields = ('name', 'registration_number')
    ordering = ('name',)