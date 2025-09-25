# Region (Wilayah) Management API

This module provides functionality for managing fishing areas/regions in the FCO system.

## API Endpoints

### Download Template

**Endpoint**: `GET /api/regions/fishing-areas/download_template/`

**Description**: Download a template file for importing fishing areas. Supports both CSV and Excel formats.

**Query Parameters**:

- `format` (optional): Specify the format of the template. Valid values are:
  - `csv` (default): Download as CSV format
  - `excel`: Download as Excel format

**Examples**:

- Download CSV template: `GET /api/regions/fishing-areas/download_template/`
- Download Excel template: `GET /api/regions/fishing-areas/download_template/?format=excel`

**Response**:

- Content-Type: `text/csv` or `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Content-Disposition: attachment with appropriate filename

### Import Fishing Areas

**Endpoint**: `POST /api/regions/fishing-areas/import_areas/`

**Description**: Import fishing areas from CSV or Excel data.

**Request Body** (multipart/form-data):

- `csv_file` (optional): Upload a CSV or Excel file containing fishing area data
- `csv_data` (optional): Send CSV data as a string
- `clear_existing` (optional): If true, delete all existing fishing areas before importing. Default is false.

**Required Fields** (in CSV/Excel):

- `nama`: Name of the fishing area (required)
- `code`: Unique code for the fishing area (required)
- `deskripsi`: Description of the fishing area (optional)

**Authentication**: Requires authentication

**Examples**:

1. Import from CSV string:

```
POST /api/regions/fishing-areas/import_areas/
Content-Type: application/json

{
  "csv_data": "nama,code,deskripsi\nArea Penangkapan Utara,APU-001,Wilayah penangkapan di utara\nArea Penangkapan Selatan,APS-002,Wilayah penangkapan di selatan",
  "clear_existing": false
}
```

2. Import from file upload:

```
POST /api/regions/fishing-areas/import_areas/
Content-Type: multipart/form-data

csv_file: [file upload]
clear_existing: false
```

**Response**:

```json
{
  "message": "Import completed",
  "created": 2,
  "updated": 0,
  "errors": 0,
  "error_details": null
}
```

## Template Format

The template contains the following columns:

- `nama`: Name of the fishing area
- `code`: Unique code identifier
- `deskripsi`: Description of the area

### Sample Data

```
nama,code,deskripsi
Area Penangkapan Utara,APU-001,Wilayah penangkapan ikan di bagian utara perairan Indonesia
Area Penangkapan Selatan,APS-002,Wilayah penangkapan ikan di bagian selatan perairan Indonesia
Area Penangkapan Timur,APT-003,Wilayah penangkapan ikan di bagian timur perairan Indonesia
```

## Supported File Formats

- **CSV**: Comma-separated values format
- **Excel**: Microsoft Excel format (.xlsx files)

Both formats are supported for both template download and import functionality.
