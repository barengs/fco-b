# Combined Fish Catch Reporting Endpoint

## Endpoint

`POST /api/catches/fish-catches-with-details/`

## Description

This endpoint allows creating a fish catch report along with its detailed species information in a single request, eliminating the need to make separate API calls for the header and details.

## Request Format

The request should include all fish catch header information along with an array of catch details:

```json
{
  "ship": 1,
  "catch_date": "2023-06-15",
  "catch_type": "pelagic",
  "location_latitude": -6.2088,
  "location_longitude": 106.8456,
  "description": "Penangkapan ikan tuna di perairan selatan",
  "catch_details": [
    {
      "fish_species": 1,
      "quantity": 150.5,
      "unit": "kg",
      "value": 1500000,
      "notes": "Tuna sirip kuning berkualitas tinggi"
    },
    {
      "fish_species": 2,
      "quantity": 75.25,
      "unit": "kg",
      "value": 750000,
      "notes": "Tuna sirip biru ukuran sedang"
    }
  ]
}
```

## Benefits

1. **Single Request**: Create both header and detail records in one API call
2. **Atomic Operation**: Either all data is saved or none (if validation fails)
3. **Reduced Network Calls**: No need to make separate requests for header and details
4. **Simplified Client Logic**: Less complex client-side code for managing related data

## Response Format

The response will include the created fish catch record with all associated details:

```json
{
  "id": 1,
  "ship": 1,
  "ship_name": "MV Sea Explorer",
  "catch_date": "2023-06-15",
  "catch_type": "pelagic",
  "location_latitude": -6.2088,
  "location_longitude": 106.8456,
  "description": "Penangkapan ikan tuna di perairan selatan",
  "created_at": "2023-06-15T10:30:00Z",
  "updated_at": "2023-06-15T10:30:00Z",
  "catch_details_display": [
    {
      "id": 1,
      "fish_catch": 1,
      "fish_species": 1,
      "fish_species_name": "Tuna Sirip Kuning",
      "quantity": 150.5,
      "unit": "kg",
      "value": 1500000,
      "notes": "Tuna sirip kuning berkualitas tinggi"
    },
    {
      "id": 2,
      "fish_catch": 1,
      "fish_species": 2,
      "fish_species_name": "Tuna Sirip Biru",
      "quantity": 75.25,
      "unit": "kg",
      "value": 750000,
      "notes": "Tuna sirip biru ukuran sedang"
    }
  ]
}
```

## Updating Records

The endpoint also supports `PUT` and `PATCH` methods for updating existing fish catch reports along with their details.
