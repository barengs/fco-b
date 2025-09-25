# API Import Wilayah Penangkapan Ikan

Dokumen ini menjelaskan cara menggunakan API untuk mengimpor data wilayah penangkapan ikan dari file CSV atau Excel.

## Endpoint

### Download Template

- **URL**: `/api/regions/fishing-areas/download_template/`
- **Method**: `GET`
- **Deskripsi**: Mengunduh template file untuk mengimpor data wilayah penangkapan ikan
- **Parameter Query**:
  - `format` (opsional): Format file template. Nilai yang valid:
    - `csv` (default): Format CSV
    - `excel`: Format Excel (.xlsx)

### Import Wilayah

- **URL**: `/api/regions/fishing-areas/import_areas/`
- **Method**: `POST`
- **Deskripsi**: Mengimpor data wilayah penangkapan ikan dari file CSV atau Excel
- **Autentikasi**: Diperlukan (hanya pengguna terautentikasi)
- **Content-Type**: `multipart/form-data` atau `application/json`

## Format Data

### Field yang Diperlukan

| Field       | Deskripsi                     | Wajib |
| ----------- | ----------------------------- | ----- |
| `nama`      | Nama wilayah penangkapan      | Ya    |
| `code`      | Kode unik wilayah             | Ya    |
| `deskripsi` | Deskripsi wilayah penangkapan | Tidak |

### Contoh Data CSV

```csv
nama,code,deskripsi
Area Penangkapan Utara,APU-001,Wilayah penangkapan ikan di bagian utara perairan Indonesia
Area Penangkapan Selatan,APS-002,Wilayah penangkapan ikan di bagian selatan perairan Indonesia
Area Penangkapan Timur,APT-003,Wilayah penangkapan ikan di bagian timur perairan Indonesia
```

## Penggunaan API

### 1. Mengunduh Template

#### Template CSV (Default)

```bash
curl -X GET "http://localhost:8000/api/regions/fishing-areas/download_template/" \
  -H "Accept: text/csv" \
  -o fishing_areas_template.csv
```

#### Template Excel

```bash
curl -X GET "http://localhost:8000/api/regions/fishing-areas/download_template/?format=excel" \
  -H "Accept: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  -o fishing_areas_template.xlsx
```

### 2. Mengimpor Data

#### Mengimpor dari File CSV

```bash
curl -X POST "http://localhost:8000/api/regions/fishing-areas/import_areas/" \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -F "csv_file=@fishing_areas.csv" \
  -F "clear_existing=false"
```

#### Mengimpor dari File Excel

```bash
curl -X POST "http://localhost:8000/api/regions/fishing-areas/import_areas/" \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -F "csv_file=@fishing_areas.xlsx" \
  -F "clear_existing=false"
```

#### Mengimpor dari Data CSV sebagai String

```bash
curl -X POST "http://localhost:8000/api/regions/fishing-areas/import_areas/" \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "csv_data": "nama,code,deskripsi\nArea Penangkapan Utara,APU-001,Wilayah penangkapan di utara\nArea Penangkapan Selatan,APS-002,Wilayah penangkapan di selatan",
    "clear_existing": false
  }'
```

## Parameter

### `clear_existing`

- **Tipe**: Boolean
- **Default**: `false`
- **Deskripsi**: Jika `true`, hapus semua data wilayah yang ada sebelum mengimpor data baru

## Respon

### Sukses

```json
{
  "message": "Import completed",
  "created": 2,
  "updated": 0,
  "errors": 0,
  "error_details": null
}
```

### Dengan Kesalahan

```json
{
  "message": "Import completed",
  "created": 1,
  "updated": 0,
  "errors": 2,
  "error_details": ["Row 2: Missing nama", "Row 3: Missing code"]
}
```

## Penanganan Kesalahan

API akan mengembalikan informasi detail tentang kesalahan yang terjadi selama proses impor:

1. **Data yang hilang**: Field yang wajib tidak diisi
2. **Kode yang duplikat**: Kode wilayah yang sudah ada
3. **Format data yang salah**: Data yang tidak sesuai dengan tipe field
4. **Kesalahan validasi**: Data yang tidak memenuhi aturan validasi

## Contoh Implementasi Python

```python
import requests

# Mengunduh template
response = requests.get('http://localhost:8000/api/regions/fishing-areas/download_template/')
with open('template.csv', 'wb') as f:
    f.write(response.content)

# Mengimpor data
files = {'csv_file': open('fishing_areas.csv', 'rb')}
headers = {'Authorization': 'Token YOUR_AUTH_TOKEN'}
data = {'clear_existing': 'false'}

response = requests.post(
    'http://localhost:8000/api/regions/fishing-areas/import_areas/',
    files=files,
    headers=headers,
    data=data
)

print(response.json())
```

## Catatan Penting

1. **Autentikasi**: Endpoint impor memerlukan autentikasi pengguna
2. **Format File**: Mendukung file CSV dan Excel (.xlsx)
3. **Unik berdasarkan Kode**: Wilayah dengan kode yang sama akan dianggap sebagai entitas yang sama
4. **Validasi Data**: API melakukan validasi data sebelum menyimpan
5. **Penanganan Duplikat**: Jika kode sudah ada, data akan diperbarui bukan dibuat baru
