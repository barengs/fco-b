# Blockchain Module Demonstration

## Overview

This document demonstrates how the blockchain module works for recording fish catch reports.

## How to Use

1. **Initialize the blockchain**:

   ```bash
   python manage.py init_blockchain
   ```

2. **Create fish catch reports**:
   When users create fish catch reports through the existing API endpoints, the blockchain module automatically records them.

3. **View blockchain data**:
   Use the API endpoints to view blockchain data:

   - `GET /api/blockchain/status/` - Check blockchain status
   - `GET /api/blockchain/transactions/` - View all transactions
   - `GET /api/blockchain/blocks/` - View all blocks

4. **Verify blockchain integrity**:
   ```bash
   python manage.py verify_blockchain
   ```

## Example Workflow

1. User submits a fish catch report through the `/api/catches/create/` endpoint
2. The [CatchDetail](file:///Users/ROFI/Develop/proyek/fco_project/catches/models.py#L23-L36) model is created
3. A Django signal automatically triggers the blockchain recording process
4. A new block is created and mined with the catch data
5. The transaction is stored in the database and linked to the block

## Data Structure

Each blockchain transaction contains:

- Ship registration number
- Fishing area code
- Fish species code
- Fish name
- Quantity and unit
- Catch date
- Timestamp

## Security Features

- **Immutability**: Once recorded, data cannot be altered
- **Verification**: Built-in integrity checking
- **Proof-of-Work**: Simple mining algorithm to secure the chain
- **Hash Chaining**: Each block references the previous block's hash

## API Examples

### Get Blockchain Status

```http
GET /api/blockchain/status/
Authorization: Token <your_token>

Response:
{
  "valid": true,
  "message": "Blockchain is valid",
  "block_count": 15,
  "transaction_count": 12
}
```

### Get Blockchain Transactions

```http
GET /api/blockchain/transactions/
Authorization: Token <your_token>

Response:
[
  {
    "id": 1,
    "fish_catch_id": 5,
    "timestamp": "2023-06-15T10:30:00Z",
    "ship_registration_number": "SHIP001",
    "fishing_area_code": "AREA001",
    "fish_species_code": "Tuna",
    "fish_name": "Yellowfin Tuna",
    "quantity": 150.5,
    "unit": "kg",
    "catch_date": "2023-06-15",
    "block_id": 3,
    "block_data": {
      "index": 3,
      "hash": "a1b2c3d4e5f...",
      "timestamp": "2023-06-15T10:30:00Z"
    }
  }
]
```

## Technical Details

### Models

1. **BlockchainBlock**: Represents a block in the blockchain
2. **FishCatchTransaction**: Represents a fish catch transaction
3. **BlockchainConfig**: Configuration settings for the blockchain

### Key Functions

1. **calculate_hash()**: Calculates the SHA256 hash for a block
2. **mine_block()**: Mines a new block with proof-of-work
3. **create_fish_catch_transaction()**: Creates a blockchain transaction for a fish catch
4. **verify_blockchain()**: Verifies the integrity of the entire blockchain

### Signals

The module uses Django signals to automatically record fish catch reports:

- When a [CatchDetail](file:///Users/ROFI/Develop/proyek/fco_project/catches/models.py#L23-L36) is created, the `add_catch_to_blockchain` signal handler is triggered
- This creates a new blockchain transaction and block

## Future Enhancements

1. **Network Distribution**: Implement a distributed network of nodes
2. **Advanced Consensus**: Use more sophisticated consensus algorithms
3. **Smart Contracts**: Add smart contract functionality
4. **Encryption**: Implement encryption for sensitive data
5. **Performance Optimization**: Optimize mining and verification processes
