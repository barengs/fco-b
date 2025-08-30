# Fish Species Import API Endpoint

## Overview

This document describes how to use the new API endpoint for importing fish species data from CSV format.

## Endpoint

**POST** `/api/fish/species/import_species/`

## Authentication

This endpoint requires authentication. Only authenticated users can import fish species data.

## Request Format

```json
{
  "csv_data": "string (required)",
  "clear_existing": "boolean (optional, default: false)"
}
```

### Parameters

- `csv_data`: A string containing CSV data with headers: `name`, `scientific_name`, `description`
- `clear_existing`: If true, all existing fish species will be deleted before importing

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

## Example Usage

### Python Requests Example

```python
import requests

# Prepare CSV data
csv_data = """name,scientific_name,description
Tuna Sirip Kuning,Thunnus albacares,Tuna dengan sirip kuning yang populer di perairan tropis
Ikan Kakap,Lutjanus campechanus,Ikan laut yang umum ditemukan di perairan hangat
Ikan Kerapu,Epinephelus spp.,Ikan batu yang bernilai ekonomi tinggi"""

# Send request
response = requests.post(
    'http://localhost:8000/api/fish/species/import_species/',
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
curl -X POST http://localhost:8000/api/fish/species/import_species/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token" \
  -d '{
    "csv_data": "name,scientific_name,description\nTuna Sirip Kuning,Thunnus albacares,Tuna dengan sirip kuning yang populer di perairan tropis\nIkan Kakap,Lutjanus campechanus,Ikan laut yang umum ditemukan di perairan hangat\nIkan Kerapu,Epinephelus spp.,Ikan batu yang bernilai ekonomi tinggi",
    "clear_existing": false
  }'
```

## Sample CSV Format

The CSV data should have the following columns:

```
name,scientific_name,description
Tuna Sirip Kuning,Thunnus albacares,Tuna dengan sirip kuning yang populer di perairan tropis
Ikan Kakap,Lutjanus campechanus,Ikan laut yang umum ditemukan di perairan hangat
```

## Error Handling

The endpoint will return appropriate HTTP status codes:

- `200 OK`: Import completed successfully
- `400 Bad Request`: Invalid CSV data or missing required parameters
- `403 Forbidden`: Authentication required

Error details will be included in the response body when applicable.
