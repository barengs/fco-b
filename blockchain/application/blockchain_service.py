"""
Blockchain Application Service (Application Layer)
Orchestrates blockchain operations.
"""

from typing import Optional, List, Dict, Any
from django.apps import apps
from datetime import datetime

from ..domain.blockchain_domain import BlockDomain, BlockchainDomainService


class BlockchainApplicationService:
    """
    Application service for blockchain operations.
    """

    def __init__(self):
        self._block_model = None
        self._transaction_model = None

    @property
    def model(self):
        if self._block_model is None:
            self._block_model = self._get_model('blockchain', 'BlockchainBlock')
        return self._block_model

    @property
    def transaction_model(self):
        if self._transaction_model is None:
            self._transaction_model = self._get_model('blockchain', 'FishCatchTransaction')
        return self._transaction_model

    def _get_model(self, app_label: str, model_name: str):
        return apps.get_model(app_label, model_name)

    def get_status(self) -> Dict[str, Any]:
        """Get overall status and verification of the blockchain."""
        verification = self.verify_chain()
        return {
            'valid': verification['valid'],
            'message': verification['message'],
            'block_count': self.model.objects.count(),
            'transaction_count': self.transaction_model.objects.count()
        }

    def get_transactions_queryset(self):
        """Get queryset of all transactions with related block."""
        return self.transaction_model.objects.select_related('block').all()

    def get_blocks_queryset(self):
        """Get queryset of all blocks."""
        return self.model.objects.all().order_by('index')

    def get_all_blocks(self) -> List[dict]:
        """Get all blocks in the blockchain."""
        blocks = self.model.objects.all().order_by('index')
        return [self._to_dict(b) for b in blocks]

    def get_latest_block(self) -> Optional[dict]:
        """Get the latest block."""
        try:
            block = self.model.objects.order_by('-index').first()
            return self._to_dict(block) if block else None
        except self.model.DoesNotExist:
            return None

    def get_block_by_index(self, index: int) -> Optional[dict]:
        """Get a block by index."""
        try:
            block = self.model.objects.get(index=index)
            return self._to_dict(block)
        except self.model.DoesNotExist:
            return None

    def add_block(self, data: str) -> dict:
        """Add a new block to the blockchain with proof of work."""
        try:
            latest = self.model.objects.order_by('-index').first()
            if latest:
                index = latest.index + 1
                previous_hash = latest.hash
            else:
                index = 0
                previous_hash = '0'

            import time
            timestamp = datetime.now().timestamp()

            nonce = 0
            while True:
                hash_value = BlockchainDomainService.calculate_hash(
                    index, previous_hash, timestamp, data, nonce
                )
                if BlockchainDomainService.is_valid_proof_of_work(hash_value):
                    break
                nonce += 1
                if nonce > 1000000:
                    return {
                        'success': False,
                        'errors': ['Proof of work tidak ditemukan']
                    }

            block = self.model.objects.create(
                index=index,
                data=data,
                previous_hash=previous_hash,
                hash=hash_value,
                nonce=nonce
            )

            return {
                'success': True,
                'data': self._to_dict(block)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }

    def verify_chain(self) -> dict:
        """Verify blockchain integrity."""
        blocks = self.model.objects.all().order_by('index')

        if not blocks.exists():
            return {
                'valid': True,
                'message': 'Blockchain kosong (tidak ada blok)'
            }

        blocks_list = list(blocks)

        for i in range(1, len(blocks_list)):
            current = blocks_list[i]
            previous = blocks_list[i - 1]

            calculated_hash = BlockchainDomainService.calculate_hash(
                current.index,
                current.previous_hash,
                current.timestamp.timestamp(),
                current.data,
                current.nonce
            )

            if current.hash != calculated_hash:
                return {
                    'valid': False,
                    'message': f'Hash tidak cocok pada blok {current.index}'
                }

            if current.previous_hash != previous.hash:
                return {
                    'valid': False,
                    'message': f'Hash sebelumnya tidak cocok pada blok {current.index}'
                }

        return {
            'valid': True,
            'message': f'Rantai blockchain valid ({len(blocks_list)} blok)'
        }

    def _to_dict(self, block) -> dict:
        """Convert model instance to dictionary."""
        return {
            'index': block.index,
            'previous_hash': block.previous_hash,
            'timestamp': block.timestamp.isoformat() if block.timestamp else None,
            'data': block.data,
            'hash': block.hash,
            'nonce': block.nonce,
        }
