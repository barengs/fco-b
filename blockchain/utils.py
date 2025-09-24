"""
Utility functions for blockchain operations
"""

import hashlib
import json
import time
from datetime import datetime
from django.db import transaction
from .models import BlockchainBlock, FishCatchTransaction
from ships.models import Quota

def calculate_hash(index, previous_hash, timestamp, data, nonce=0):
    """Calculate the hash for a block"""
    value = str(index) + str(previous_hash) + str(timestamp) + str(data) + str(nonce)
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def create_genesis_block():
    """Create the genesis block (first block in the blockchain)"""
    if BlockchainBlock.objects.exists():
        return BlockchainBlock.objects.first()
    
    genesis_data = "Genesis Block - FCO Blockchain System"
    genesis_hash = calculate_hash(0, "0", time.time(), genesis_data)
    
    genesis_block = BlockchainBlock.objects.create(
        index=0,
        data=genesis_data,
        previous_hash="0",
        hash=genesis_hash,
        nonce=0
    )
    
    return genesis_block

def get_latest_block():
    """Get the latest block in the blockchain"""
    return BlockchainBlock.objects.order_by('-index').first()

def mine_block(block_data, difficulty=2):
    """Mine a new block with proof of work"""
    latest_block = get_latest_block()
    if not latest_block:
        latest_block = create_genesis_block()
    
    index = latest_block.index + 1
    previous_hash = latest_block.hash
    timestamp = time.time()
    
    nonce = 0
    prefix = '0' * difficulty
    
    while True:
        hash_result = calculate_hash(index, previous_hash, timestamp, block_data, nonce)
        if hash_result.startswith(prefix):
            return {
                'index': index,
                'previous_hash': previous_hash,
                'timestamp': timestamp,
                'data': block_data,
                'hash': hash_result,
                'nonce': nonce
            }
        nonce += 1

def add_block_to_chain(block_data):
    """Add a new block to the blockchain"""
    mined_block = mine_block(block_data)
    
    block = BlockchainBlock.objects.create(
        index=mined_block['index'],
        data=mined_block['data'],
        previous_hash=mined_block['previous_hash'],
        hash=mined_block['hash'],
        nonce=mined_block['nonce']
    )
    
    return block

def create_fish_catch_transaction(fish_catch, catch_detail, quota=None):
    """Create a blockchain transaction for a fish catch report"""
    # Get the latest block or create genesis block
    latest_block = get_latest_block()
    if not latest_block:
        latest_block = create_genesis_block()

    # Prepare transaction data
    transaction_data = {
        'ship_registration_number': fish_catch.ship.registration_number,
        'fishing_area_code': getattr(fish_catch, 'fishing_area_code', 'N/A'),
        'fish_species_code': catch_detail.fish_species.name,  # Using name as code
        'fish_name': catch_detail.fish_species.name,
        'quantity': float(catch_detail.quantity),
        'unit': catch_detail.unit,
        'catch_date': fish_catch.catch_date.isoformat(),
        'quota_amount': float(quota.quota) if quota else None,
        'quota_remaining': float(quota.remaining_quota) if quota else None,
        'timestamp': datetime.now().isoformat()
    }

    # Convert to JSON string for storage in block
    block_data = json.dumps(transaction_data, sort_keys=True)

    # Add block to chain
    block = add_block_to_chain(block_data)

    # Create the transaction record
    transaction_record = FishCatchTransaction.objects.create(
        fish_catch=fish_catch,
        block=block,
        ship_registration_number=fish_catch.ship.registration_number,
        fishing_area_code=getattr(fish_catch, 'fishing_area_code', 'N/A'),
        fish_species_code=catch_detail.fish_species.name,
        fish_name=catch_detail.fish_species.name,
        quantity=catch_detail.quantity,
        unit=catch_detail.unit,
        catch_date=fish_catch.catch_date,
        quota=quota
    )

    return transaction_record

def verify_blockchain():
    """Verify the integrity of the blockchain"""
    blocks = BlockchainBlock.objects.order_by('index')
    
    for i in range(1, len(blocks)):
        current_block = blocks[i]
        previous_block = blocks[i-1]
        
        # Verify hash
        calculated_hash = calculate_hash(
            current_block.index,
            current_block.previous_hash,
            current_block.timestamp.timestamp(),
            current_block.data,
            current_block.nonce
        )
        
        if current_block.hash != calculated_hash:
            return False, f"Invalid hash at block {current_block.index}"
        
        # Verify previous hash
        if current_block.previous_hash != previous_block.hash:
            return False, f"Invalid previous hash at block {current_block.index}"
    
    return True, "Blockchain is valid"