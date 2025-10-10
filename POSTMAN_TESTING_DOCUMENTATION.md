# Dokumentasi Testing Postman - Sistem Manajemen Tangkapan Ikan FCO

## Gambaran Umum

Dokumentasi ini menyediakan panduan lengkap untuk testing API Sistem Manajemen Tangkapan Ikan FCO menggunakan Postman, mulai dari registrasi pengguna hingga operasi lengkap sistem.

## Base URL
```
http://localhost:8000/api/
```

## Flow Testing Lengkap

### 1. REGISTRASI PENGGUNA

#### 1.1 Registrasi Owner (Pemilik Kapal)
**Endpoint:** `POST /auth/register/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "username": "owner_test",
    "email": "owner@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "role": "owner",
    "full_name": "Budi Santoso",
    "contact_info": "Jl. Pelabuhan No. 123",
    "address": "Jakarta Utara",
    "phone": "081234567890"
}
```

**Response Expected (201):**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user_id": 1,
    "username": "owner_test",
    "role": "owner",
    "profile": {
        "type": "owner",
        "full_name": "Budi Santoso",
        "contact_info": "Jl. Pelabuhan No. 123",
        "address": "Jakarta Utara",
        "phone": "081234567890",
        "email": "owner@example.com"
    }
}
```

#### 1.2 Registrasi Captain (Nahkoda)
**Endpoint:** `POST /auth/register/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "username": "captain_test",
    "email": "captain@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "role": "captain",
    "full_name": "Andi Wijaya",
    "contact_info": "Jl. Nelayan No. 456",
    "address": "Surabaya",
    "phone": "081234567891",
    "ship_code": "SHIP001"
}
```

**Response Expected (201):**
```json
{
    "token": "8844b09199c62bcf9418ad846dd0e4bbdfc6ee4c",
    "user_id": 2,
    "username": "captain_test",
    "role": "captain",
    "profile": {
        "type": "captain",
        "full_name": "Andi Wijaya",
        "contact_info": "Jl. Nelayan No. 456",
        "address": "Surabaya",
        "phone": "081234567891",
        "email": "captain@example.com",
        "license_number": "LIC2"
    }
}
```

#### 1.3 Registrasi Admin
**Endpoint:** `POST /auth/register/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "username": "admin_test",
    "email": "admin@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "role": "admin",
    "full_name": "Siti Nurhaliza",
    "phone": "081234567892"
}
```

**Response Expected (201):**
```json
{
    "token": "7744b09199c62bcf9418ad846dd0e4bbdfc6ee4d",
    "user_id": 3,
    "username": "admin_test",
    "role": "admin",
    "profile": {
        "type": "admin",
        "full_name": "Siti Nurhaliza",
        "email": "admin@example.com",
        "phone": "081234567892",
        "department": "Administrator",
        "position": "Administrator"
    }
}
```

### 2. LOGIN PENGGUNA

#### 2.1 Login Owner
**Endpoint:** `POST /auth/login/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "username": "owner_test",
    "password": "password123"
}
```

**Response Expected (200):**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 1,
    "username": "owner_test",
    "user_as": "owner",
    "roles": ["owner"],
    "profile": {
        "type": "owner",
        "name": "Budi Santoso",
        "owner_type": "individual",
        "email": "owner@example.com",
        "phone": "081234567890",
        "address": "Jakarta Utara"
    }
}
```

#### 2.2 Login Captain
**Endpoint:** `POST /auth/login/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "username": "captain_test",
    "password": "password123"
}
```

**Response Expected (200):**
```json
{
    "token": "8844b09199c62bcf9418ad846dd0e4bbdfc6ee4c",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 2,
    "username": "captain_test",
    "user_as": "captain",
    "roles": ["captain"],
    "profile": {
        "type": "captain",
        "name": "Andi Wijaya",
        "license_number": "LIC2",
        "email": "captain@example.com",
        "phone": "081234567891",
        "address": "Surabaya",
        "years_of_experience": null
    }
}
```

### 3. REFRESH TOKEN

**Endpoint:** `POST /auth/refresh/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response Expected (200):**
```json
{
    "token": "new_token_here",
    "refresh_token": "new_refresh_token_here"
}
```

### 4. MANAJEMEN KAPAL

#### 4.1 Cek Registrasi Kapal
**Endpoint:** `GET /ships/check-ship/?registration_number=SHIP001`

**Headers:**
```
Content-Type: application/json
```

**Response Expected (200):**
```json
{
    "exists": true,
    "ship": {
        "id": 1,
        "name": "Kapal Nelayan 1",
        "registration_number": "SHIP001",
        "owner": "Budi Santoso",
        "captain": "Andi Wijaya"
    }
}
```

#### 4.2 Buat Kapal Baru
**Endpoint:** `POST /ships/ships/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Body (JSON):**
```json
{
    "name": "Kapal Nelayan Sejahtera",
    "registration_number": "SHIP002",
    "owner": 1,
    "captain": 2,
    "length": 25.5,
    "width": 6.2,
    "gross_tonnage": 150.0,
    "year_built": 2020,
    "home_port": "Pelabuhan Jakarta",
    "active": true
}
```

**Response Expected (201):**
```json
{
    "id": 2,
    "name": "Kapal Nelayan Sejahtera",
    "registration_number": "SHIP002",
    "owner": {
        "id": 1,
        "full_name": "Budi Santoso",
        "owner_type": "individual"
    },
    "captain": {
        "id": 2,
        "full_name": "Andi Wijaya",
        "license_number": "LIC2"
    },
    "length": "25.50",
    "width": "6.20",
    "gross_tonnage": "150.00",
    "year_built": 2020,
    "home_port": "Pelabuhan Jakarta",
    "active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 4.3 Import Kapal dari CSV
**Endpoint:** `POST /ships/ships/import_ships/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Body (JSON):**
```json
{
    "csv_data": "name,registration_number,owner_name,captain_name,length,width,gross_tonnage,year_built,home_port,active\nKapal Test 1,SHIP003,Budi Santoso,Andi Wijaya,20.5,5.2,100.5,2020,Port A,true\nKapal Test 2,SHIP004,Budi Santoso,,15.0,4.0,75.0,2018,Port B,true",
    "clear_existing": false
}
```

**Response Expected (200):**
```json
{
    "message": "Import completed",
    "created": 2,
    "updated": 0,
    "errors": 0,
    "error_details": null
}
```

#### 4.4 Daftar Semua Kapal
**Endpoint:** `GET /ships/ships/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response Expected (200):**
```json
[
    {
        "id": 1,
        "name": "Kapal Nelayan 1",
        "registration_number": "SHIP001",
        "owner": {
            "id": 1,
            "full_name": "Budi Santoso",
            "owner_type": "individual"
        },
        "captain": {
            "id": 2,
            "full_name": "Andi Wijaya",
            "license_number": "LIC2"
        },
        "length": "20.00",
        "width": "5.00",
        "gross_tonnage": "100.00",
        "year_built": 2019,
        "home_port": "Jakarta",
        "active": true
    }
]
```

### 5. MANAJEMEN SPESIES IKAN

#### 5.1 Buat Spesies Ikan
**Endpoint:** `POST /fish/fish-species/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Body (JSON):**
```json
{
    "name": "Tuna Sirip Kuning",
    "scientific_name": "Thunnus albacares",
    "description": "Tuna dengan sirip kuning yang populer di perairan tropis"
}
```

**Response Expected (201):**
```json
{
    "id": 1,
    "name": "Tuna Sirip Kuning",
    "scientific_name": "Thunnus albacares",
    "description": "Tuna dengan sirip kuning yang populer di perairan tropis",
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
}
```

#### 5.2 Import Spesies Ikan dari CSV
**Endpoint:** `POST /fish/fish-species/import_species/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Body (JSON):**
```json
{
    "csv_data": "name,scientific_name,description\nIkan Kakap,Lutjanus campechanus,Ikan laut yang umum ditemukan di perairan hangat\nIkan Kerapu,Epinephelus spp,Ikan karang yang bernilai ekonomi tinggi",
    "clear_existing": false
}
```

**Response Expected (200):**
```json
{
    "message": "Import completed successfully",
    "created": 2,
    "updated": 0,
    "errors": 0
}
```

#### 5.3 Daftar Spesies Ikan
**Endpoint:** `GET /fish/fish-species/`

**Headers:**
```
Content-Type: application/json
```

**Response Expected (200):**
```json
[
    {
        "id": 1,
        "name": "Tuna Sirip Kuning",
        "scientific_name": "Thunnus albacares",
        "description": "Tuna dengan sirip kuning yang populer di perairan tropis",
        "created_at": "2024-01-15T10:35:00Z",
        "updated_at": "2024-01-15T10:35:00Z"
    },
    {
        "id": 2,
        "name": "Ikan Kakap",
        "scientific_name": "Lutjanus campechanus",
        "description": "Ikan laut yang umum ditemukan di perairan hangat",
        "created_at": "2024-01-15T10:36:00Z",
        "updated_at": "2024-01-15T10:36:00Z"
    }
]
```

### 6. MANAJEMEN AREA PENANGKAPAN

#### 6.1 Buat Area Penangkapan
**Endpoint:** `POST /regions/fishing-areas/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Body (JSON):**
```json
{
    "nama": "Area Penangkapan Utara",
    "code": "APU-001",
    "deskripsi": "Wilayah penangkapan di utara Jawa",
    "boundary_coordinates": "[[10.0, 20.0], [10.5, 20.5], [11.0, 21.0]]"
}
```

**Response Expected (201):**
```json
{
    "id": 1,
    "nama": "Area Penangkapan Utara",
    "code": "APU-001",
    "deskripsi": "Wilayah penangkapan di utara Jawa",
    "boundary_coordinates": "[[10.0, 20.0], [10.5, 20.5], [11.0, 21.0]]",
    "created_at": "2024-01-15T10:40:00Z",
    "updated_at": "2024-01-15T10:40:00Z"
}
```

#### 6.2 Import Area Penangkapan dari CSV
**Endpoint:** `POST /regions/fishing-areas/import_areas/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Body (JSON):**
```json
{
    "csv_data": "name,code,description,boundary_coordinates\nArea Penangkapan Selatan,APS-002,Wilayah penangkapan di selatan Jawa,\"[[15.0, 25.0], [15.5, 25.5]]\"\nArea Penangkapan Timur,APT-003,Wilayah penangkapan di timur Jawa,\"[[20.0, 30.0], [20.5, 30.5]]\"",
    "clear_existing": false
}
```

**Response Expected (200):**
```json
{
    "message": "Import completed successfully",
    "created": 2,
    "updated": 0,
    "errors": 0
}
```

### 7. MANAJEMEN TANGKAPAN IKAN

#### 7.1 Buat Laporan Tangkapan Sederhana
**Endpoint:** `POST /catches/fish-catches/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 8844b09199c62bcf9418ad846dd0e4bbdfc6ee4c
```

**Body (JSON):**
```json
{
    "ship": 1,
    "catch_date": "2024-01-15",
    "location_latitude": -6.2088,
    "location_longitude": 106.8456,
    "total_weight": 150.5,
    "total_value": 2500000,
    "catch_type":"pelagic", 
    "fishing_areas": [1],
    "notes": "Tangkapan hari ini cukup baik"
}
```

**Response Expected (201):**
```json
{
    "id": 1,
    "ship": {
        "id": 1,
        "name": "Kapal Nelayan 1",
        "registration_number": "SHIP001"
    },
    "catch_date": "2024-01-15",
    "location_latitude": "-6.20880000",
    "location_longitude": "106.84560000",
    "total_weight": "150.50",
    "total_value": "2500000.00",
    "fishing_areas": [
        {
            "id": 1,
            "nama": "Area Penangkapan Utara",
            "code": "APU-001"
        }
    ],
    "notes": "Tangkapan hari ini cukup baik",
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
}
```

#### 7.2 Buat Detail Tangkapan
**Endpoint:** `POST /catches/catch-details/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 8844b09199c62bcf9418ad846dd0e4bbdfc6ee4c
```

**Body (JSON):**
```json
{
    "fish_catch": 1,
    "fish_species": 1,
    "quantity": 25,
    "weight": 75.5,
    "value": 1500000,
    "notes": "Tuna kualitas baik"
}
```

**Response Expected (201):**
```json
{
    "id": 1,
    "fish_catch": 1,
    "fish_species": {
        "id": 1,
        "name": "Tuna Sirip Kuning",
        "scientific_name": "Thunnus albacares"
    },
    "quantity": 25,
    "weight": "75.50",
    "value": "1500000.00",
    "notes": "Tuna kualitas baik",
    "created_at": "2024-01-15T11:05:00Z",
    "updated_at": "2024-01-15T11:05:00Z"
}
```

#### 7.3 Buat Laporan Tangkapan dengan Detail (Combined)
**Endpoint:** `POST /catches/fish-catches-with-details/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 8844b09199c62bcf9418ad846dd0e4bbdfc6ee4c
```

**Body (JSON):**
```json
{
    "ship": 1,
    "catch_date": "2024-01-16",
    "catch_type" : "pelagic",
    "location_latitude": -6.3088,
    "location_longitude": 106.9456,
    "fishing_areas": [1, 2],
    "notes": "Tangkapan dengan berbagai spesies",
    "catch_details": [
        {
            "fish_species": 1,
            "quantity": 15,
            "weight": 45.0,
            "value": 900000,
            "notes": "Tuna segar"
        },
        {
            "fish_species": 2,
            "quantity": 30,
            "weight": 60.0,
            "value": 800000,
            "notes": "Kakap merah"
        }
    ]
}
```

**Response Expected (201):**
```json
{
    "id": 2,
    "ship": {
        "id": 1,
        "name": "Kapal Nelayan 1",
        "registration_number": "SHIP001"
    },
    "catch_date": "2024-01-16",
    "location_latitude": "-6.30880000",
    "location_longitude": "106.94560000",
    "total_weight": "105.00",
    "total_value": "1700000.00",
    "fishing_areas": [
        {
            "id": 1,
            "nama": "Area Penangkapan Utara",
            "code": "APU-001"
        },
        {
            "id": 2,
            "nama": "Area Penangkapan Selatan",
            "code": "APS-002"
        }
    ],
    "notes": "Tangkapan dengan berbagai spesies",
    "catch_details": [
        {
            "id": 2,
            "fish_species": {
                "id": 1,
                "name": "Tuna Sirip Kuning",
                "scientific_name": "Thunnus albacares"
            },
            "quantity": 15,
            "weight": "45.00",
            "value": "900000.00",
            "notes": "Tuna segar"
        },
        {
            "id": 3,
            "fish_species": {
                "id": 2,
                "name": "Ikan Kakap",
                "scientific_name": "Lutjanus campechanus"
            },
            "quantity": 30,
            "weight": "60.00",
            "value": "800000.00",
            "notes": "Kakap merah"
        }
    ],
    "created_at": "2024-01-16T09:00:00Z",
    "updated_at": "2024-01-16T09:00:00Z"
}
```

### 8. PREDIKSI KUOTA KAPAL (AI/ML)

#### 8.1 Prediksi Kuota Kapal
**Endpoint:** `POST /ships/predict-quota/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Body (JSON):**
```json
{
  "ship_registration_number": "SHIP002",
  "prediction_months": 12,
  "algorithm": "both"
}

**Response Expected (200):**
```json
{
    "ship_registration_number": "SHIP002",
    "ship_name": "Kapal Nelayan Sejahtera",
    "prediction_period": "12 bulan ke depan",
    "lstm_predictions": [
        {
            "date": "2025-10-13",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        },
        {
            "date": "2025-11-12",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        },
        {
            "date": "2025-12-12",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        },
        {
            "date": "2026-01-11",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        },
        {
            "date": "2026-02-10",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        },
        {
            "date": "2026-03-12",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        },
        {
            "date": "2026-04-11",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        },
        {
            "date": "2026-05-11",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        },
        {
            "date": "2026-06-10",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        },
        {
            "date": "2026-07-10",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        },
        {
            "date": "2026-08-09",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        },
        {
            "date": "2026-09-08",
            "predicted_quota": 45.0,
            "confidence_interval": [
                45.0,
                45.0
            ]
        }
    ],
    "nsga3_predictions": [
        {
            "date": "2025-10-13",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        },
        {
            "date": "2025-11-12",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        },
        {
            "date": "2025-12-12",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        },
        {
            "date": "2026-01-11",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        },
        {
            "date": "2026-02-10",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        },
        {
            "date": "2026-03-12",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        },
        {
            "date": "2026-04-11",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        },
        {
            "date": "2026-05-11",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        },
        {
            "date": "2026-06-10",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        },
        {
            "date": "2026-07-10",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        },
        {
            "date": "2026-08-09",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        },
        {
            "date": "2026-09-08",
            "predicted_quota": 45.0,
            "fitness_score": 1.0
        }
    ],
    "recommendation": {
        "quota": 45
    }
}
```

#### 8.2 Input Manual Kuota oleh Regulator
**Endpoint:** `POST /ships/regulator/manual-quota/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 7744b09199c62bcf9418ad846dd0e4bbdfc6ee4d
```

**Body (JSON):**
```json
{
  "ship_registration_number": "SHIP002",
  "year": 2025,
  "quota_amount": "80"
}
```
{
  "ship_registration_number": "string",
  "year": 2050,
  "quota_amount": "-80"
}
**Response Expected (201):**
```json
{
    "ship_registration_number": "SHIP002",
    "ship_name": "Kapal Nelayan Sejahtera",
    "year": 2025,
    "quota_amount": 80.0,
    "remaining_quota": 80.0,
    "message": "Kuota untuk kapal Kapal Nelayan Sejahtera tahun 2025 berhasil dibuat dengan jumlah 80.00 kg"
}
```

### 9. REKOMENDASI AI KAPAL

#### 9.1 Rekomendasi Kapal Terbaik
**Endpoint:** `GET /ships/ai-recommendations/?time_period=180&fish_species=1&top_n=5`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response Expected (200):**
```json
{
    "top_ships": [
        {
            "id": 1,
            "name": "Kapal Nelayan 1",
            "registration_number": "SHIP001",
            "owner": "Budi Santoso",
            "captain": "Andi Wijaya",
            "total_catch": 1250.75,
            "average_catch": 125.08,
            "catch_trend": "naik",
            "catch_efficiency": 106.25,
            "best_fishing_location": {
                "latitude": -6.2088,
                "longitude": 106.8456
            },
            "best_fishing_months": ["January", "February", "March"]
        }
    ],
    "analysis_period": "2023-07-19 to 2024-01-15",
    "recommendation_factors": "Total tangkapan, rata-rata tangkapan per laporan, tren tangkapan, dan lokasi terbaik",
    "total_ships_analyzed": 3
}
```

### 10. BLOCKCHAIN TRACKING

#### 10.1 Status Blockchain
**Endpoint:** `GET /blockchain/status/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response Expected (200):**
```json
{
    "blockchain_active": true,
    "total_blocks": 156,
    "total_transactions": 423,
    "last_block_hash": "00000a1b2c3d4e5f6789abcdef123456789abcdef",
    "last_block_timestamp": "2024-01-15T13:00:00Z",
    "network_status": "healthy"
}
```

#### 10.2 Daftar Transaksi Blockchain
**Endpoint:** `GET /blockchain/transactions/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response Expected (200):**
```json
[
    {
        "id": 1,
        "transaction_hash": "tx_abc123def456",
        "transaction_type": "fish_catch",
        "ship_id": 1,
        "catch_id": 1,
        "timestamp": "2024-01-15T11:00:00Z",
        "block_number": 155,
        "verified": true
    },
    {
        "id": 2,
        "transaction_hash": "tx_def456ghi789",
        "transaction_type": "quota_assignment",
        "ship_id": 1,
        "quota_id": 1,
        "timestamp": "2024-01-15T12:30:00Z",
        "block_number": 156,
        "verified": true
    }
]
```

#### 10.3 Daftar Blok Blockchain
**Endpoint:** `GET /blockchain/blocks/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response Expected (200):**
```json
[
    {
        "block_number": 156,
        "block_hash": "00000a1b2c3d4e5f6789abcdef123456789abcdef",
        "previous_hash": "00000b2c3d4e5f6789abcdef123456789abcdef12",
        "timestamp": "2024-01-15T13:00:00Z",
        "transaction_count": 3,
        "merkle_root": "merkle_root_hash_here",
        "nonce": 12345
    },
    {
        "block_number": 155,
        "block_hash": "00000b2c3d4e5f6789abcdef123456789abcdef12",
        "previous_hash": "00000c3d4e5f6789abcdef123456789abcdef1234",
        "timestamp": "2024-01-15T12:45:00Z",
        "transaction_count": 2,
        "merkle_root": "merkle_root_hash_here_2",
        "nonce": 67890
    }
]
```

### 11. MANAJEMEN ADMIN

#### 11.1 Buat Role Baru
**Endpoint:** `POST /admin/roles/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 7744b09199c62bcf9418ad846dd0e4bbdfc6ee4d
```

**Body (JSON):**
```json
{
    "name": "inspector",
    "description": "Petugas inspeksi lapangan",
    "permissions": ["view_catches", "verify_catches", "create_reports"]
}
```

**Response Expected (201):**
```json
{
    "id": 1,
    "name": "inspector",
    "description": "Petugas inspeksi lapangan",
    "permissions": ["view_catches", "verify_catches", "create_reports"],
    "created_at": "2024-01-15T14:00:00Z",
    "updated_at": "2024-01-15T14:00:00Z"
}
```

#### 11.2 Assign Role ke User
**Endpoint:** `POST /admin/user-roles/assign_role/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 7744b09199c62bcf9418ad846dd0e4bbdfc6ee4d
```

**Body (JSON):**
```json
{
    "user_id": 2,
    "role_id": 1,
    "assigned_by": 3,
    "notes": "Penugasan sebagai inspector untuk wilayah Jakarta"
}
```

**Response Expected (201):**
```json
{
    "id": 1,
    "user": {
        "id": 2,
        "username": "captain_test",
        "full_name": "Andi Wijaya"
    },
    "role": {
        "id": 1,
        "name": "inspector",
        "description": "Petugas inspeksi lapangan"
    },
    "assigned_by": {
        "id": 3,
        "username": "admin_test",
        "full_name": "Siti Nurhaliza"
    },
    "assigned_at": "2024-01-15T14:15:00Z",
    "notes": "Penugasan sebagai inspector untuk wilayah Jakarta"
}
```

### 12. LAPORAN DAN ANALYTICS

#### 12.1 Laporan Tangkapan Kapal
**Endpoint:** `GET /ships/ships/1/catch_reports/`

**Headers:**
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response Expected (200):**
```json
[
    {
        "id": 1,
        "catch_date": "2024-01-15",
        "location_latitude": "-6.20880000",
        "location_longitude": "106.84560000",
        "total_weight": "150.50",
        "total_value": "2500000.00",
        "fishing_areas": [
            {
                "id": 1,
                "nama": "Area Penangkapan Utara",
                "code": "APU-001"
            }
        ],
        "catch_details": [
            {
                "id": 1,
                "fish_species": {
                    "id": 1,
                    "name": "Tuna Sirip Kuning",
                    "scientific_name": "Thunnus albacares"
                },
                "quantity": 25,
                "weight": "75.50",
                "value": "1500000.00"
            }
        ]
    }
]
```

#### 12.2 Filter Tangkapan berdasarkan Tanggal
**Endpoint:** `GET /catches/fish-catches/?start_date=2024-01-01&end_date=2024-01-31&ship_id=1`

**Headers:**
```
Content-Type: application/json
Authorization: Token 8844b09199c62bcf9418ad846dd0e4bbdfc6ee4c
```

**Response Expected (200):**
```json
[
    {
        "id": 1,
        "ship": {
            "id": 1,
            "name": "Kapal Nelayan 1",
            "registration_number": "SHIP001"
        },
        "catch_date": "2024-01-15",
        "location_latitude": "-6.20880000",
        "location_longitude": "106.84560000",
        "total_weight": "150.50",
        "total_value": "2500000.00",
        "fishing_areas": [
            {
                "id": 1,
                "nama": "Area Penangkapan Utara",
                "code": "APU-001"
            }
        ],
        "notes": "Tangkapan hari ini cukup baik"
    }
]
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
    "error": "Invalid data provided",
    "details": {
        "field_name": ["This field is required."]
    }
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
    "detail": "Not found."
}
```

#### 500 Internal Server Error
```json
{
    "error": "Internal server error occurred"
}
```

## Tips Testing

1. **Urutan Testing**: Ikuti urutan yang disediakan untuk memastikan data dependencies terpenuhi
2. **Token Management**: Simpan token dari response login untuk digunakan di request selanjutnya
3. **Environment Variables**: Gunakan Postman environment untuk menyimpan base URL dan token
4. **Data Cleanup**: Gunakan parameter `clear_existing=true` saat import untuk membersihkan data test
5. **Error Testing**: Test juga skenario error dengan data yang tidak valid
6. **Pagination**: Untuk endpoint list, test juga dengan parameter pagination jika tersedia

## Collection Postman

Untuk kemudahan, buat collection Postman dengan folder-folder berikut:
- 01_Authentication (Register, Login, Refresh)
- 02_Ships_Management (CRUD, Import, Check)
- 03_Fish_Species (CRUD, Import)
- 04_Fishing_Areas (CRUD, Import)
- 05_Fish_Catches (CRUD, Combined)
- 06_AI_ML_Features (Predictions, Recommendations)
- 07_Blockchain (Status, Transactions, Blocks)
- 08_Admin_Management (Roles, Users, Permissions)
- 09_Reports_Analytics (Filters, Statistics)

Setiap folder berisi request yang sesuai dengan urutan testing yang optimal.