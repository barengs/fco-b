# Fitur Autentikasi untuk Sistem FCO

## Gambaran Umum

Fitur autentikasi ini memungkinkan nahkoda (captain) atau pemilik kapal (owner) untuk masuk ke sistem menggunakan salah satu dari dua metode:

1. **Username** - Metode tradisional menggunakan username dan password
2. **Nomor Registrasi Kapal** - Metode alternatif menggunakan nomor registrasi kapal dan password

## Implementasi Teknis

### 1. Backend Autentikasi Kustom

File: `owners/authentication.py`

Backend autentikasi kustom yang mengimplementasikan logika:

- Pertama mencoba mencocokkan input sebagai username
- Jika tidak ditemukan, mencoba mencocokkan input sebagai nomor registrasi kapal
- Untuk kapal yang ditemukan, mencari pengguna yang terkait (pemilik atau nahkoda)
- Memverifikasi password dan mengembalikan pengguna yang berhasil diautentikasi

### 2. Endpoint API

**URL:** `POST /api/owners/login/`

**Deskripsi:** Endpoint untuk login pengguna dengan username atau nomor registrasi kapal

**Request Body:**

```json
{
  "username": "string", // Bisa berupa username atau nomor registrasi kapal
  "password": "string"
}
```

**Response:**

```json
{
  "token": "string", // Token autentikasi untuk penggunaan di header Authorization
  "user_id": "integer", // ID pengguna
  "username": "string", // Username pengguna
  "is_owner": "boolean", // Apakah pengguna adalah pemilik kapal
  "is_captain": "boolean" // Apakah pengguna adalah nahkoda
}
```

### 3. Konfigurasi

**File:** `fco_project/settings.py`

- Menambahkan `rest_framework.authtoken` ke `INSTALLED_APPS`
- Mengkonfigurasi `AUTHENTICATION_BACKENDS` untuk menggunakan backend kustom
- Mengatur `DEFAULT_AUTHENTICATION_CLASSES` untuk menggunakan token authentication

## Cara Penggunaan

### 1. Login dengan Username

```bash
curl -X POST http://localhost:8000/api/owners/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### 2. Login dengan Nomor Registrasi Kapal

```bash
curl -X POST http://localhost:8000/api/owners/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "SHIP001",
    "password": "shippassword"
  }'
```

### 3. Menggunakan Token untuk Request Berikutnya

Setelah login berhasil, gunakan token dalam header Authorization untuk request berikutnya:

```bash
curl -X GET http://localhost:8000/api/ships/ \
  -H "Authorization: Token your_token_here"
```

## Keamanan

- Menggunakan token authentication yang aman
- Password disimpan dengan hashing yang aman
- Backend autentikasi kustom hanya mengembalikan pengguna yang berhasil diverifikasi
- Mendukung semua fitur keamanan bawaan Django

## Catatan Penting

- Pastikan setiap kapal memiliki nomor registrasi yang unik
- Setiap pemilik atau nahkoda harus memiliki akun pengguna (CustomUser) yang terkait
- Token yang diberikan harus disimpan dengan aman di sisi klien
