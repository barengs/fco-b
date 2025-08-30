# Fishing Areas Import API Endpoint

## Overview

This document describes how to use the new API endpoint for importing fishing area data from CSV format.

## Endpoint

**POST** `/api/regions/fishing-areas/import_areas/`

## Authentication

This endpoint requires authentication. Only authenticated users can import fishing area data.

## Request Format

```json
{
  "csv_data": "string (required)",
  "clear_existing": "boolean (optional, default: false)"
}
```

### Parameters

- `csv_data`: A string containing CSV data with headers: `name,code,description,boundary_coordinates`
- `clear_existing`: If true, all existing fishing areas will be deleted before importing

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

- `name`: Name of the fishing area (required)
- `code`: Code of the fishing area (required, unique)
- `description`: Description of the fishing area (optional)
- `boundary_coordinates`: Boundary coordinates of the fishing area (optional, can be JSON or text representation)

## Example Usage

### Python Requests Example

```python
import requests

# Prepare CSV data
csv_data = """name,code,description,boundary_coordinates
Area Penangkapan Utara,APU-001,Wilayah penangkapan di utara,"[[10.0, 20.0], [10.5, 20.5]]"
Area Penangkapan Selatan,APS-002,Wilayah penangkapan di selatan,"[[15.0, 25.0], [15.5, 25.5]]"""

# Send request
response = requests.post(
    'http://localhost:8000/api/regions/fishing-areas/import_areas/',
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
curl -X POST http://localhost:8000/api/regions/fishing-areas/import_areas/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token" \
  -d '{
    "csv_data": "name,code,description,boundary_coordinates\nArea Penangkapan Utara,APU-001,Wilayah penangkapan di utara,\"[[10.0, 20.0], [10.5, 20.5]]\"\nArea Penangkapan Selatan,APS-002,Wilayah penangkapan di selatan,\"[[15.0, 25.0], [15.5, 25.5]]\"",
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

1. `name` and `code` are required
2. `code` must be unique
3. All fishing areas will be validated according to the FishingArea model constraints
