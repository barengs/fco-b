"""
Serializers for blockchain models
"""

from rest_framework import serializers
from .models import FishCatchTransaction, BlockchainBlock

class BlockchainBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockchainBlock
        fields = ['index', 'timestamp', 'data', 'previous_hash', 'hash', 'nonce']

class FishCatchTransactionSerializer(serializers.ModelSerializer):
    block_data = serializers.SerializerMethodField()
    
    class Meta:
        model = FishCatchTransaction
        fields = [
            'id',
            'fish_catch_id',
            'timestamp',
            'ship_registration_number',
            'fishing_area_code',
            'fish_species_code',
            'fish_name',
            'quantity',
            'unit',
            'catch_date',
            'block_id',
            'block_data'
        ]
    
    def get_block_data(self, obj):
        return {
            'index': obj.block.index,
            'hash': obj.block.hash,
            'timestamp': obj.block.timestamp
        }