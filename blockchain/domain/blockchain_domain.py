"""
Blockchain Domain Model (Domain Layer)
Domain logic for blockchain entities.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BlockDomain:
    """Domain entity representing a blockchain block."""
    
    index: int
    previous_hash: str
    data: str
    hash: str
    nonce: int = 0
    timestamp: str = ''

    def is_valid(self) -> bool:
        """Validate block integrity."""
        return bool(self.index >= 0) and bool(self.previous_hash) and bool(self.hash)


class BlockchainDomainService:
    """Domain service for blockchain business rules."""

    DIFFICULTY_PREFIX = '0' * 4  # 4 leading zeros for proof of work

    @classmethod
    def validate_block_data(cls, index: int, previous_hash: str,
                           data: str, nonce: int = 0,
                           hash_value: str = '') -> dict:
        """Validate block data."""
        errors = []

        if index < 0:
            errors.append('Index harus non-negatif')

        if not previous_hash:
            errors.append('Previous hash wajib diisi')

        if not data:
            errors.append('Data wajib diisi')

        if not hash_value:
            errors.append('Hash wajib diisi')

        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }

    @classmethod
    def calculate_hash(cls, index: int, previous_hash: str,
                      timestamp: float, data: str, nonce: int = 0) -> str:
        """Calculate SHA-256 hash for block data."""
        import hashlib
        payload = f"{index}{previous_hash}{timestamp}{data}{nonce}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    @classmethod
    def is_valid_proof_of_work(cls, block_hash: str) -> bool:
        """Check if hash meets proof of work difficulty."""
        return block_hash.startswith(cls.DIFFICULTY_PREFIX)
