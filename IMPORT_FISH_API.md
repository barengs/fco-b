# Fish Import API Endpoint

## Overview

This document describes how to use the new API endpoint for importing individual fish data from CSV format.

## Endpoint

**POST** `/api/fish/fish/import_fish/`

## Authentication

This endpoint requires authentication. Only authenticated users can import fish data.

## Request Format

```json
{
  "csv_data": "string (required)",
  "clear_existing": "boolean (optional, default: false)"
}
```

### Parameters

- `csv_data`: A string containing CSV data with headers: `species_name,name,length,weight,notes`
- `clear_existing`: If true, all existing fish will be deleted before importing

## Response Format

```json
{
  "message": "Import completed",
  "created": 0,
  "updated": 0,
  "errors": 0,
  "error_details": []
}
```

## CSV Format

The CSV data must include the following headers:

- `species_name`: Name of the fish species (required, must match an existing species)
- `name`: Name of the individual fish (optional)
- `length`: Length of the fish in cm (optional, numeric)
- `weight`: Weight of the fish in kg (optional, numeric)
- `notes`: Additional notes about the fish (optional)

## Example Usage

### Python Requests Example

```python
import requests

# Prepare CSV data
csv_data = """species_name,name,length,weight,notes
Tuna Sirip Kuning,Budi,120.5,30.2,Ikan tangkapan pertama
Ikan Kakap,Andi,30.0,2.5,Ikan ukuran sedang"""

# Send request
response = requests.post(
    'http://localhost:8000/api/fish/fish/import_fish/',
    json={
        'csv_data': csv_data,
        'clear_existing': False
    },
    headers={
        'Authorization': 'Token your-auth-token'
    }
)

print(response.json())
```

### cURL Example

```bash
curl -X POST http://localhost:8000/api/fish/fish/import_fish/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token" \
  -d '{
    "csv_data": "species_name,name,length,weight,notes\nTuna Sirip Kuning,Budi,120.5,30.2,Ikan tangkapan pertama\nIkan Kakap,Andi,30.0,2.5,Ikan ukuran sedang",
    "clear_existing": false
  }'
```

## Error Handling

The endpoint will return appropriate HTTP status codes:

- `200 OK`: Import completed successfully
- `400 Bad Request`: Invalid CSV data or missing required parameters
- `403 Forbidden`: Authentication required

Error details will be included in the response body when applicable.

## Validation Rules

1. `species_name` is required and must match an existing fish species
2. `length` and `weight` must be valid numeric values if provided
3. All fish will be validated according to the Fish model constraints
