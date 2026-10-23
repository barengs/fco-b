# Dokumentasi Resmi API Backend FCO (Fish Chain Optima)

Dokumentasi lengkap REST API backend Django REST Framework untuk ekosistem **Fish Chain Optima (FCO)**. Mencakup format permintaan (*request*), parameter wajib/opsional, dan contoh respon (*response*) sukses maupun galat dalam Bahasa Indonesia.

---

## 1. Informasi Dasar & Autentikasi

- **Base URL Pengembangan**: `http://localhost:8000/api/`
- **Base URL Produksi**: `https://api.fishpro.id/api/`
- **Format Pertukaran Data**: `application/json` (Kecuali untuk endpoint impor file CSV/Excel: `multipart/form-data`)

### Header Permintaan Standar
Untuk endpoint yang membutuhkan autentikasi (*authenticated*), sertakan token autentikasi pada header HTTP:
```http
Authorization: Token <token_pengguna_anda>
Content-Type: application/json
```

---

## 2. Modul Autentikasi (`/api/auth/`)

### A. Registrasi Pengguna Baru
Mendaftarkan akun baru berdasarkan peran (*Role*): `owner`, `captain`, `admin`, atau `regulator`.

- **Metode**: `POST`
- **URL**: `/api/auth/register/`
- **Autentikasi**: Tidak diperlukan (*Public*)

#### Request Body (JSON)
```json
{
  "username": "nahkoda_budi",
  "email": "budi@email.com",
  "password": "PasswordRahasia123!",
  "password_confirm": "PasswordRahasia123!",
  "role": "captain",
  "full_name": "Budi Santoso",
  "phone": "081234567890",
  "contact_info": "081234567890",
  "owner_type": "individual",
  "ship_code": "REG-2026-0412",
  "address": "Pelabuhan Muara Baru, Jakarta"
}
```

| Field | Tipe | Wajib | Keterangan |
| :--- | :--- | :--- | :--- |
| `username` | String | Ya | Nama pengguna unik (min. 3 karakter) |
| `email` | String | Ya | Alamat email aktif |
| `password` | String | Ya | Kata sandi (min. 8 karakter) |
| `password_confirm` | String | Ya | Konfirmasi kata sandi (harus sama) |
| `role` | String | Ya | Pilihan: `owner`, `captain`, `admin`, `regulator` |
| `full_name` | String | Ya | Nama lengkap legal pendaftar |
| `phone` | String | Opsional | Nomor telepon / WhatsApp |
| `owner_type` | String | Opsional | `individual` (Perorangan) atau `company` (Perusahaan) |
| `ship_code` | String | Opsional | Nomor registrasi kapal yang terafiliasi |
| `address` | String | Opsional | Alamat domisili atau pelabuhan asal |

#### Response Sukses (`201 Created`)
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 14,
  "username": "nahkoda_budi",
  "email": "budi@email.com",
  "role": "captain",
  "message": "Registrasi berhasil"
}
```

#### Response Galat (`400 Bad Request`)
```json
{
  "username": ["Pengguna dengan nama ini sudah terdaftar."],
  "password_confirm": ["Konfirmasi kata sandi tidak cocok."]
}
```

---

### B. Masuk / Login Pengguna
- **Metode**: `POST`
- **URL**: `/api/auth/login/`
- **Autentikasi**: Tidak diperlukan

#### Request Body (JSON)
```json
{
  "username": "nahkoda_budi",
  "password": "PasswordRahasia123!"
}
```

#### Response Sukses (`200 OK`)
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 14,
  "username": "nahkoda_budi",
  "email": "budi@email.com",
  "role": "captain",
  "roles": ["captain"],
  "user_as": "captain",
  "profile": {
    "name": "Budi Santoso",
    "full_name": "Budi Santoso",
    "license_number": "LIC14",
    "role": "captain"
  }
}
```

---

## 3. Modul Armada Kapal & Kuota AI (`/api/ships/`)

### A. Daftar Semua Kapal
- **Metode**: `GET`
- **URL**: `/api/ships/ships/`
- **Parameter Query (Opsional)**:
  - `search`: Filter teks untuk nama kapal atau nomor registrasi SIPI.
  - `owner_id`: Filter kapal milik pemilik tertentu.
- **Autentikasi**: `Token`

#### Response Sukses (`200 OK`)
```json
[
  {
    "id": 1,
    "name": "KM Samudra Jaya",
    "registration_number": "REG-2026-0412",
    "owner": 1,
    "owner_name": "makdum pribadi",
    "captain": 2,
    "captain_name": "makdum nahkoda",
    "gross_tonnage": 85.0,
    "length": 28.0,
    "width": 6.8,
    "year_built": 2019,
    "home_port": "Pelabuhan Muara Baru, Jakarta",
    "active": true,
    "current_year_quota": {
      "id": 1,
      "year": 2026,
      "total_quota": 20000.0,
      "used_quota": 200.0,
      "remaining_quota": 19800.0,
      "quota_percentage": 99.0
    }
  }
]
```

---

### B. Pendaftaran Kapal Baru
- **Metode**: `POST`
- **URL**: `/api/ships/ships/`
- **Autentikasi**: `Token` (Admin / Owner)

#### Request Body (JSON)
```json
{
  "name": "KM Bahari Sentosa",
  "registration_number": "SIPI-2026-9901",
  "owner": 1,
  "captain": 2,
  "gross_tonnage": 45.5,
  "length": 21.0,
  "width": 5.2,
  "year_built": 2021,
  "home_port": "Pelabuhan Benoa, Bali",
  "active": true
}
```

#### Response Sukses (`201 Created`)
```json
{
  "id": 5,
  "name": "KM Bahari Sentosa",
  "registration_number": "SIPI-2026-9901",
  "owner": 1,
  "owner_name": "makdum pribadi",
  "captain": 2,
  "captain_name": "makdum nahkoda",
  "gross_tonnage": 45.5,
  "length": 21.0,
  "width": 5.2,
  "year_built": 2021,
  "home_port": "Pelabuhan Benoa, Bali",
  "active": true
}
```

---

### C. Prediksi Kuota AI (LSTM + NSGA-III)
Menghitung rekomendasi kuota lestari berbasis deret waktu tangkapan historis (LSTM) dan optimasi multi-objektif kelestarian perairan (NSGA-III).

- **Metode**: `POST`
- **URL**: `/api/ships/predict-quota/`
- **Autentikasi**: `Token` (Regulator / Admin)

#### Request Body (JSON)
```json
{
  "ship_registration_number": "REG-2026-0412",
  "prediction_months": 12,
  "epoch_level": 5
}
```

#### Response Sukses (`200 OK`)
```json
{
  "ship_registration_number": "REG-2026-0412",
  "ship_name": "KM Samudra Jaya",
  "predicted_quota": 13800.0,
  "recommended_quota": 13800.0,
  "nsga_optimized_quota": 13800.0,
  "lstm_predicted_quota": 14200.0,
  "confidence": 0.945,
  "training_time": "0.38s",
  "epoch_used": 20,
  "lstm_predictions": [
    { "date": "2026-11", "predicted_value": 1150.0 },
    { "date": "2026-12", "predicted_value": 1200.0 }
  ],
  "nsga_optimized": [
    { "date": "2026-11", "optimized_value": 1100.0 },
    { "date": "2026-12", "optimized_value": 1150.0 }
  ]
}
```

---

### D. Penyesuaian Kuota Manual Regulator
- **Metode**: `POST`
- **URL**: `/api/ships/regulator-manual-quota/`
- **Autentikasi**: `Token` (Regulator / Admin)

#### Request Body (JSON)
```json
{
  "ship_registration_number": "REG-2026-0412",
  "year": 2026,
  "quota_amount": 25000.0
}
```

#### Response Sukses (`200 OK`)
```json
{
  "status": "success",
  "message": "Kuota resmi kapal REG-2026-0412 tahun 2026 berhasil disesuaikan.",
  "data": {
    "ship_registration_number": "REG-2026-0412",
    "year": 2026,
    "total_quota": 25000.0,
    "remaining_quota": 24800.0
  }
}
```

---

## 4. Modul Terminal Timbangan Pintar IoT (`/api/iot/`)

### A. Mengirim Bobot Sensor Hardware (Dari Perangkat IoT)
- **Metode**: `POST`
- **URL**: `/api/iot/receive-weight/`
- **Header Khusus**: `X-Device-Token: <api_key_perangkat>`

#### Request Body (JSON)
```json
{
  "device_id": "DERMAGA-TEST-1",
  "weight": 85.50,
  "unit": "kg",
  "tare": 0.0,
  "is_stable": true
}
```

#### Response Sukses (`201 Created`)
```json
{
  "status": "success",
  "reading_id": "e9a03977-2e11-477f-a63e-64cbe3911b6f",
  "message": "Data berat berhasil dicatat",
  "timestamp": "2026-10-23T01:10:00Z"
}
```

---

### B. Ambil Pembacaan Timbangan Aktif
Mengambil data berat terkini yang belum diproses (*pending*).

- **Metode**: `GET`
- **URL**: `/api/iot/latest/?device_id=DERMAGA-TEST-1&status=pending`
- **Autentikasi**: `Token`

#### Response Sukses (`200 OK`)
```json
{
  "id": "e9a03977-2e11-477f-a63e-64cbe3911b6f",
  "device_id": "DERMAGA-TEST-1",
  "scale_name": "Timbangan Dermaga 1",
  "port_name": "Pelabuhan Muara Baru",
  "weight": 85.50,
  "unit": "kg",
  "tare": 0.0,
  "is_stable": true,
  "status": "pending",
  "created_at": "2026-10-23T01:10:00Z"
}
```
*(Catatan: Jika belum ada beban yang ditimbang, backend merespon `200 OK` dengan payload `null` atau `404` tanpa memutus aplikasi).*

---

### C. Simpan Tangkapan Resmi Pelabuhan (IoT + Kuota + PNBP + Blockchain)
Mentautkan berat timbangan fisik ke kapal pembongkar, memotong kuota tahunan kapal secara otomatis, menghitung tarif resmi PNBP, dan menyegel transaksi ke blok blockchain SHA-256.

- **Metode**: `POST`
- **URL**: `/api/iot/save-catch/`
- **Autentikasi**: `Token` (Regulator / Admin)

#### Request Body (JSON)
```json
{
  "reading_id": "e9a03977-2e11-477f-a63e-64cbe3911b6f",
  "ship_registration_number": "REG-2026-0412",
  "fish_species_id": 1,
  "catch_type": "pelagic",
  "catch_date": "2026-10-23",
  "operator_notes": "Kondisi ikan segar ber-es, kualitas ekspor prima."
}
```

#### Response Sukses (`201 Created`)
```json
{
  "status": "success",
  "message": "Laporan tangkapan berhasil disimpan dan disegel ke blockchain",
  "catch_id": 42,
  "weight": 85.50,
  "unit": "kg",
  "pnbp": 85500.0,
  "blockchain_status": "Tersegel (Blok #2)"
}
```

---

## 5. Modul Laporan Tangkapan Ikan (`/api/catches/`)

### A. Buat Laporan Tangkapan Manual Lengkap (Multi-Spesies)
- **Metode**: `POST`
- **URL**: `/api/catches/fish-catches-with-details/`
- **Autentikasi**: `Token`

#### Request Body (JSON)
```json
{
  "ship": "REG-2026-0412",
  "catch_date": "2026-10-23",
  "catch_type": "pelagic",
  "location_latitude": "-8.740000",
  "location_longitude": "115.200000",
  "description": "Hasil operasi laut selatan Jawa",
  "catch_details": [
    {
      "fish_species": 1,
      "quantity": 250.0,
      "unit": "kg",
      "value": 3750000.0,
      "notes": "Tongkol super"
    },
    {
      "fish_species": 2,
      "quantity": 100.0,
      "unit": "kg",
      "value": 2000000.0,
      "notes": "Cakalang segar"
    }
  ]
}
```

#### Response Sukses (`201 Created`)
```json
{
  "id": 43,
  "ship": "REG-2026-0412",
  "ship_name": "KM Samudra Jaya",
  "catch_date": "2026-10-23",
  "catch_type": "pelagic",
  "location_latitude": "-8.740000",
  "location_longitude": "115.200000",
  "description": "Hasil operasi laut selatan Jawa",
  "created_at": "2026-10-23T01:15:00Z",
  "catch_details": [
    {
      "id": 101,
      "fish_species": 1,
      "fish_species_name": "Tongkol",
      "quantity": 250.0,
      "unit": "kg",
      "pnbp": 250000.0
    },
    {
      "id": 102,
      "fish_species": 2,
      "fish_species_name": "Cakalang",
      "quantity": 100.0,
      "unit": "kg",
      "pnbp": 100000.0
    }
  ]
}
```

---

## 6. Modul Buku Besar Blockchain (`/api/blockchain/`)

### A. Validasi Status Rantai Kriptografis
- **Metode**: `GET`
- **URL**: `/api/blockchain/status/`
- **Autentikasi**: `Token`

#### Response Sukses (`200 OK`)
```json
{
  "valid": true,
  "message": "Rantai blockchain valid",
  "total_blocks": 2,
  "last_block": {
    "index": 1,
    "hash": "00367446e1654157140f8cb92e1fe04c55209f87c24f601b3d2ff90333934d22",
    "timestamp": "2026-10-20T13:17:26Z"
  }
}
```

---

### B. Ambil Semua Blok Rantai
- **Metode**: `GET`
- **URL**: `/api/blockchain/blocks/`
- **Autentikasi**: `Token`

#### Response Sukses (`200 OK`)
```json
[
  {
    "index": 0,
    "hash": "e027f46f41e57c66cb1e405e324036814bca81c1c9116ebcf88a18357013cef5",
    "previous_hash": "0",
    "timestamp": "2026-10-20T13:17:26Z",
    "data": "Genesis Block",
    "nonce": 0
  },
  {
    "index": 1,
    "hash": "00367446e1654157140f8cb92e1fe04c55209f87c24f601b3d2ff90333934d22",
    "previous_hash": "e027f46f41e57c66cb1e405e324036814bca81c1c9116ebcf88a18357013cef5",
    "timestamp": "2026-10-20T13:17:26Z",
    "data": "Block containing 1 transactions",
    "nonce": 31
  }
]
```

---

### C. Ambil Transaksi Tangkapan Tersegel
- **Metode**: `GET`
- **URL**: `/api/blockchain/transactions/`
- **Autentikasi**: `Token`

#### Response Sukses (`200 OK`)
```json
[
  {
    "id": 1,
    "ship_registration_number": "REG-2026-0412",
    "fishing_area_code": "573",
    "fish_name": "Ikan Lele",
    "quantity": 200.0,
    "unit": "kg",
    "block_id": 1,
    "timestamp": "2026-10-20T13:17:26Z",
    "block_data": {
      "index": 1,
      "hash": "00367446e1654157140f8cb92e1fe04c55209f87c24f601b3d2ff90333934d22"
    }
  }
]
```

---

## 7. Modul Pemilik & Nahkoda (`/api/owners/`)

### A. Daftar Pemilik Resmi (Tanpa Data Dummy)
Mengambil daftar pemilik kapal terdaftar resmi. Otomatis menyaring data dummy `Owner of ...`.

- **Metode**: `GET`
- **URL**: `/api/owners/owners/?search=makdum`
- **Autentikasi**: `Token`

#### Response Sukses (`200 OK`)
```json
[
  {
    "id": 1,
    "full_name": "makdum pribadi",
    "owner_type": "individual",
    "contact_info": "92394234",
    "email": "makdumibrohim23@test.com",
    "phone": "92394234",
    "address": "Jakarta",
    "ships": [
      {
        "id": 1,
        "name": "KM Samudra Jaya",
        "registration_number": "REG-2026-0412",
        "active": true
      }
    ]
  }
]
```

---

## 8. Modul Impor Data CSV/Excel

Endpoint untuk mengunggah berkas data massal:

| Modul | Endpoint | Format Header Kolom Wajib | Nama Unduhan Template |
| :--- | :--- | :--- | :--- |
| **Wilayah (WPP)** | `POST /api/regions/fishing-areas/import_areas/` | `nama,code,deskripsi` | `template_impor_wpp_nri.csv` |
| **Spesies Ikan** | `POST /api/fish/fish-species/import_species/` | `name,scientific_name,description` | `template_impor_spesies_ikan.csv` |
| **Sampel Ikan** | `POST /api/fish/fish/import_fish/` | `nama_jenis,nama_ikan,berat_kg,catatan` | `template_impor_sampel_timbangan_ikan.csv` |
| **Kapal Armada** | `POST /api/ships/ships/import_ships/` | `name,registration_number,owner_name,...` | `template_impor_kapal_armada.csv` |

#### Format Body Impor (`multipart/form-data`)
- `csv_file`: Berkas CSV atau Excel (.xlsx) dengan encoding UTF-8.
- `clear_existing`: `true` atau `false` (Apakah menghapus data lama sebelum diimpor).

#### Response Sukses Impor (`200 OK`)
```json
{
  "message": "Data wilayah WPP berhasil diimpor",
  "created": 11,
  "updated": 0,
  "errors": 0,
  "error_details": null
}
```
