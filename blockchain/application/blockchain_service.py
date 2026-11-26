"""
Blockchain Application Service (Application Layer)
Orchestrates blockchain operations.
"""

import logging
from typing import Optional, List, Dict, Any
from django.apps import apps
from datetime import datetime

from ..domain.blockchain_domain import BlockDomain, BlockchainDomainService

logger = logging.getLogger(__name__)


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
                        'errors': ['Validasi proof of work melebihi batas percobaan.']
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
                'data': self._to_dict(block),
                'block': block
            }
        except Exception:
            logger.exception("Gagal menambahkan blok baru ke blockchain")
            return {
                'success': False,
                'errors': ['Gagal menambahkan blok ke blockchain.']
            }

    def record_catch_transaction(self, fish_catch) -> List[Any]:
        """
        Record a fish catch and its details into a newly mined cryptographic block.
        Creates corresponding FishCatchTransaction entries linked to the block.
        """
        import json
        from django.db import transaction

        details = list(fish_catch.catch_details.all().select_related('fish_species', 'wpp'))
        if not details:
            return []

        # Find active quota for this ship and year
        quota_model = self._get_model('ships', 'Quota')
        quota_obj = quota_model.objects.filter(
            ship=fish_catch.ship,
            year=fish_catch.catch_date.year,
            is_active=True
        ).first()

        # Build payload summarizing the catch report
        block_summary = {
            'catch_id': fish_catch.id,
            'ship_registration': fish_catch.ship.registration_number,
            'ship_name': fish_catch.ship.name,
            'catch_date': fish_catch.catch_date.isoformat(),
            'catch_type': fish_catch.catch_type,
            'latitude': str(fish_catch.location_latitude),
            'longitude': str(fish_catch.location_longitude),
            'items': [
                {
                    'species': d.fish_species.name,
                    'quantity': float(d.quantity),
                    'unit': d.unit,
                    'wpp': d.wpp.code if d.wpp else 'WPP-RI',
                    'pnbp': float(d.pnbp) if d.pnbp else 0.0,
                }
                for d in details
            ]
        }

        # Add block to the chain (with SHA-256 Proof of Work)
        block_result = self.add_block(json.dumps(block_summary, sort_keys=True))
        if not block_result.get('success'):
            return []

        block_instance = block_result.get('block')
        created_transactions = []

        with transaction.atomic():
            for detail in details:
                tx = self.transaction_model.objects.create(
                    fish_catch=fish_catch,
                    block=block_instance,
                    ship_registration_number=fish_catch.ship.registration_number,
                    fishing_area_code=detail.wpp.code if detail.wpp else "WPP-RI",
                    fish_species_code=getattr(detail.fish_species, 'code', None) or f"FISH-{detail.fish_species.id}",
                    fish_name=detail.fish_species.name,
                    quantity=detail.quantity,
                    unit=detail.unit,
                    catch_date=fish_catch.catch_date,
                    tarif_index=detail.tarif_index,
                    pnkp=detail.pnkp,
                    pnbp=detail.pnbp,
                    quota=quota_obj
                )
                created_transactions.append(tx)

        return created_transactions

    def verify_chain(self) -> dict:
        """Verify blockchain integrity."""
        blocks = self.model.objects.all().order_by('index')

        if not blocks.exists():
            return {
                'valid': True,
                'message': 'Belum ada blok yang tercatat di blockchain.'
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
                    'message': f'Integritas blok #{current.index} tidak sesuai (hash berubah).'
                }

            if current.previous_hash != previous.hash:
                return {
                    'valid': False,
                    'message': f'Rantai hash pada blok #{current.index} tidak tersambung dengan blok sebelumnya.'
                }

        return {
            'valid': True,
            'message': f'Seluruh rantai blok valid ({len(blocks_list)} blok).'
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
