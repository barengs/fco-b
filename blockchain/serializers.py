"""
Serializers for blockchain models
"""

from rest_framework import serializers
from .models import FishCatchTransaction, BlockchainBlock
from ships.models import Quota

class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quota
        fields = ['id', 'year', 'quota', 'remaining_quota']

class BlockchainBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockchainBlock
        fields = ['index', 'timestamp', 'data', 'previous_hash', 'hash', 'nonce']

class FishCatchTransactionSerializer(serializers.ModelSerializer):
    block_data = serializers.SerializerMethodField()
    quota = QuotaSerializer(read_only=True)

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
            'quota',
            'block_id',
            'block_data'
        ]

    def get_block_data(self, obj):
        return {
            'index': obj.block.index,
            'hash': obj.block.hash,
            'timestamp': obj.block.timestamp
        }

