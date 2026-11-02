"""
Blockchain Domain Entity & Rules (Domain Layer)
Pure cryptographic hashing logic and proof-of-work validation rules.
"""

import hashlib
from typing import Any

class BlockEntity:
    """Domain model logic for cryptographic block hashing and proof-of-work."""

    @staticmethod
    def calculate_hash(index: int, previous_hash: str, timestamp: float, data: Any, nonce: int = 0) -> str:
        payload = f"{index}{previous_hash}{timestamp}{data}{nonce}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    @staticmethod
    def is_valid_proof_of_work(block_hash: str, difficulty: int) -> bool:
        prefix = '0' * difficulty
        return block_hash.startswith(prefix)
