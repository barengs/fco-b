# Ship Import Template Download API Endpoint

## Overview

This document describes how to use the new API endpoint for downloading a CSV template that can be used for importing ship data.

## Endpoint

**GET** `/api/ships/ships/download_template/`

## Authentication

This endpoint does not require authentication. It is publicly accessible.

## Response Format

The endpoint returns a CSV file with the following headers:

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

The CSV file will include one example row with placeholder values to help users understand the expected format.

## Example Usage

### Python Requests Example

```python
import requests

# Download template
response = requests.get('http://localhost:8000/api/ships/ships/download_template/')

# Save to file
with open('ship_import_template.csv', 'wb') as f:
    f.write(response.content)

print("Template downloaded successfully!")
```

### cURL Example

```bash
curl -X GET http://localhost:8000/api/ships/ships/download_template/ \
  -o ship_import_template.csv
```

### Browser Access

You can also access the endpoint directly in a web browser:

```
http://localhost:8000/api/ships/ships/download_template/
```

The browser will prompt you to download the CSV file.

## CSV Template Structure

The downloaded CSV file will have the following structure:

```csv
name,registration_number,owner_name,captain_name,length,width,gross_tonnage,year_built,home_port,active
Nama Kapal,REG001,Nama Pemilik,Nama Nahkoda,20.5,5.2,100.5,2020,Pelabuhan Asal,true
```

## Usage Instructions

1. Download the template CSV file using this endpoint
2. Open the file in a spreadsheet application (Excel, Google Sheets, etc.)
3. Replace the example data with your actual ship data
4. Save the file as CSV
5. Use the saved CSV file with the ship import endpoint (`/api/ships/ships/import_ships/`)

## Error Handling

The endpoint should always return a valid CSV file. If there are any issues, appropriate HTTP status codes will be returned:

- `200 OK`: Template downloaded successfully
- `500 Internal Server Error`: Server error occurred

## Notes

- The template includes one example row to help users understand the expected format
- All text fields should be enclosed in quotes if they contain commas or special characters
- Numeric fields should not include units (e.g., just "20.5" not "20.5 meters")
- Date fields should be in standard format (e.g., "2020" for year)
- Boolean fields should use "true" or "false" (case insensitive)
