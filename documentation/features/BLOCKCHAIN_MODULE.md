# Blockchain Module for Fish Catch Reports

## Overview

This module implements a simple blockchain system to record fish catch reports in an immutable ledger. Every time a user submits a fish catch report, the relevant data is automatically added to the blockchain.

## Features

1. **Automatic Recording**: Fish catch reports are automatically added to the blockchain when created
2. **Immutable Storage**: Once data is recorded in the blockchain, it cannot be altered
3. **Verification**: Built-in verification system to check blockchain integrity
4. **API Endpoints**: RESTful API endpoints to access blockchain data
5. **Admin Interface**: Django admin interface for viewing blockchain data

## Data Recorded in Blockchain

For each fish catch report, the following data is recorded in the blockchain:

- Ship registration number
- Fishing area code
- Fish species code
- Fish name
- Quantity and unit
- Catch date
- Timestamp of recording

## How It Works

1. **Genesis Block**: The blockchain starts with a genesis block that serves as the anchor
2. **Automatic Recording**: When a [CatchDetail](file:///Users/ROFI/Develop/proyek/fco_project/catches/models.py#L23-L36) object is created, a Django signal automatically creates a blockchain transaction
3. **Block Creation**: Each transaction is stored in a new block with proof-of-work mining
4. **Hash Chain**: Each block contains the hash of the previous block, creating an immutable chain
5. **Verification**: The system can verify the integrity of the entire blockchain

## Models

### BlockchainBlock

Represents a block in the blockchain:

- `index`: Position in the blockchain
- `timestamp`: When the block was created
- `data`: The transaction data (JSON string)
- `previous_hash`: Hash of the previous block
- `hash`: Hash of this block
- `nonce`: Number used for proof-of-work

### FishCatchTransaction

Represents a fish catch transaction recorded in the blockchain:

- `fish_catch`: Reference to the original catch report
- `block`: Reference to the blockchain block
- `timestamp`: When the transaction was recorded
- `ship_registration_number`: Ship's registration number
- `fishing_area_code`: Code of the fishing area
- `fish_species_code`: Code of the fish species
- `fish_name`: Name of the fish
- `quantity`: Quantity caught
- `unit`: Unit of measurement
- `catch_date`: Date of the catch

## API Endpoints

- `GET /api/blockchain/status/`: Get blockchain status and verification
- `GET /api/blockchain/transactions/`: Get all fish catch transactions
- `GET /api/blockchain/blocks/`: Get all blocks in the blockchain

## Management Commands

- `python manage.py init_blockchain`: Initialize the blockchain with a genesis block
- `python manage.py verify_blockchain`: Verify the integrity of the blockchain

## Implementation Details

The blockchain implementation is simplified for demonstration purposes:

- Uses proof-of-work with a simple hash prefix requirement
- Stores block data as JSON strings
- Automatically triggered by Django signals
- Verification checks hash integrity and chain continuity

## Security Considerations

This is a simplified implementation for educational purposes:

- Not suitable for production use without significant enhancements
- Lacks advanced consensus mechanisms
- Does not include network distribution
- Mining difficulty is fixed and low

For production use, consider integrating with established blockchain platforms.
