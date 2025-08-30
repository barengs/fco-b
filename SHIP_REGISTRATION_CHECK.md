# Fitur Pemeriksaan Registrasi Kapal

## Gambaran Umum

Fitur ini memungkinkan pengguna (pemilik kapal atau nahkoda) untuk memeriksa apakah nomor registrasi kapal sudah terdaftar dalam sistem sebelum melakukan pendaftaran. Ini membantu mencegah duplikasi data dan memastikan integritas data dalam sistem.

## Endpoint API

**URL:** `GET /api/ships/check-ship/`

**Deskripsi:** Memeriksa apakah nomor registrasi kapal terdaftar dalam sistem

**Parameter:**

- `registration_number` (string, wajib) - Nomor registrasi kapal yang akan diperiksa

## Respons

### Jika Kapal Ditemukan (HTTP 200)

```json
{
  "exists": true,
  "ship": {
    "id": 1,
    "name": "Nama Kapal",
    "registration_number": "SHIP001",
    "owner": "Nama Pemilik",
    "captain": "Nama Nahkoda"
  }
}
```

### Jika Kapal Tidak Ditemukan (HTTP 404)

```json
{
  "exists": false,
  "message": "Nomor registrasi tidak ditemukan"
}
```

### Jika Parameter Tidak Lengkap (HTTP 400)

```json
{
  "exists": false,
  "message": "Parameter registration_number diperlukan"
}
```

## Cara Penggunaan

### Contoh Permintaan dengan cURL

```bash
curl -X GET "http://localhost:8000/api/ships/check-ship/?registration_number=SHIP001"
```

### Contoh Respons Sukses

```json
{
  "exists": true,
  "ship": {
    "id": 1,
    "name": "Kapal Tangkapan Ikan Maju",
    "registration_number": "SHIP001",
    "owner": "PT Perikanan Nusantara",
    "captain": "Budi Santoso"
  }
}
```

### Contoh Respons Tidak Ditemukan

```json
{
  "exists": false,
  "message": "Nomor registrasi tidak ditemukan"
}
```

## Integrasi dengan Proses Pendaftaran

Fitur ini sebaiknya digunakan sebagai langkah awal dalam proses pendaftaran pemilik kapal atau nahkoda:

1. Pengguna memasukkan nomor registrasi kapal
2. Sistem memeriksa apakah nomor tersebut sudah terdaftar
3. Jika sudah terdaftar, sistem menampilkan informasi kapal
4. Jika belum terdaftar, sistem dapat mengarahkan pengguna untuk mendaftarkan kapal terlebih dahulu

## Keamanan

- Endpoint ini dapat diakses tanpa autentikasi untuk memudahkan proses pemeriksaan awal
- Tidak mengekspos informasi sensitif selain nama kapal, pemilik, dan nahkoda
- Mengikuti praktik keamanan standar Django REST Framework

## Catatan Penting

- Nomor registrasi kapal bersifat unik dalam sistem
- Pemeriksaan bersifat case-sensitive
- Endpoint ini hanya melakukan pencarian berdasarkan nomor registrasi, bukan berdasarkan nama kapal atau informasi lainnya
