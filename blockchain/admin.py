from django.contrib import admin
from .models import BlockchainBlock, FishCatchTransaction, BlockchainConfig

@admin.register(BlockchainBlock)
class BlockchainBlockAdmin(admin.ModelAdmin):
    list_display = ('index', 'timestamp', 'hash', 'previous_hash')
    readonly_fields = ('index', 'timestamp', 'hash', 'previous_hash', 'nonce')
    search_fields = ('hash', 'previous_hash')

@admin.register(FishCatchTransaction)
class FishCatchTransactionAdmin(admin.ModelAdmin):
    list_display = ('ship_registration_number', 'fish_name', 'fishing_area_code', 'timestamp')
    list_filter = ('timestamp', 'fishing_area_code', 'fish_species_code')
    search_fields = ('ship_registration_number', 'fish_name', 'fishing_area_code')
    readonly_fields = ('timestamp',)

@admin.register(BlockchainConfig)
class BlockchainConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    search_fields = ('name',)