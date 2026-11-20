# Ship Import API Endpoint

## Overview

This document describes how to use the new API endpoint for importing ship data from CSV format.

## Endpoints

### Import Ships

**POST** `/api/ships/ships/import_ships/`

### Download Template

**GET** `/api/ships/ships/download_template/`

Download a CSV template that can be used for importing ship data. This endpoint does not require authentication.

## Authentication

The import endpoint requires authentication. Only authenticated users can import ship data.
The template download endpoint does not require authentication.

## Request Format (Import)

```json
{
  "csv_data": "string (required)",
  "clear_existing": "boolean (optional, default: false)"
}
```

### Parameters

- `csv_data`: A string containing CSV data with headers: `name,registration_number,owner_name,captain_name,length,width,gross_tonnage,year_built,home_port,active`
- `clear_existing`: If true, all existing ships will be deleted before importing

## Response Format (Import)

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

- `name`: Name of the ship (required)
- `registration_number`: Registration number of the ship (required, unique)
- `owner_name`: Name of the ship owner (required, must match an existing owner)
- `captain_name`: Name of the ship captain (optional)
- `length`: Length of the ship in meters (optional, numeric)
- `width`: Width of the ship in meters (optional, numeric)
- `gross_tonnage`: Gross tonnage of the ship (optional, numeric)
- `year_built`: Year the ship was built (optional, integer)
- `home_port`: Home port of the ship (optional)
- `active`: Whether the ship is active (optional, boolean: true/false, default: true)

## Example Usage

### Download Template

To download the CSV template:

```bash
curl -X GET http://localhost:8000/api/ships/ships/download_template/ \
  -o ship_import_template.csv
```

### Python Requests Example (Import)

```python
import requests

# Prepare CSV data
csv_data = """name,registration_number,owner_name,captain_name,length,width,gross_tonnage,year_built,home_port,active
Test Ship 1,SHIP001,Test Owner,Test Captain,20.5,5.2,100.5,2020,Port A,true
Test Ship 2,SHIP002,Test Owner,,15.0,4.0,75.0,2018,Port B,true"""

# Send request
response = requests.post(
    'http://localhost:8000/api/ships/ships/import_ships/',
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

### cURL Example (Import)

```bash
curl -X POST http://localhost:8000/api/ships/ships/import_ships/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token" \
  -d '{
    "csv_data": "name,registration_number,owner_name,captain_name,length,width,gross_tonnage,year_built,home_port,active\nTest Ship 1,SHIP001,Test Owner,Test Captain,20.5,5.2,100.5,2020,Port A,true\nTest Ship 2,SHIP002,Test Owner,,15.0,4.0,75.0,2018,Port B,true",
    "clear_existing": false
  }'
```

## Error Handling

The import endpoint will return appropriate HTTP status codes:

- `200 OK`: Import completed successfully
- `400 Bad Request`: Invalid CSV data or missing required parameters
- `403 Forbidden`: Authentication required

Error details will be included in the response body when applicable.

## Validation Rules

1. `name`, `registration_number`, and `owner_name` are required
2. `registration_number` must be unique
3. `owner_name` must match an existing owner
4. `captain_name` must match an existing captain if provided
5. `length`, `width`, `gross_tonnage` must be valid numeric values if provided
6. `year_built` must be a valid integer if provided
7. `active` must be a valid boolean value (true/false, 1/0, yes/no, y/n) if provided
8. All ships will be validated according to the Ship model constraints
