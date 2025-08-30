# Implementasi Serializers Owner dan Captain dengan Data Kapal Terkait

## Gambaran Umum

Implementasi ini meningkatkan Sistem Manajemen Tangkapan Ikan FCO dengan menambahkan fungsionalitas untuk mengambil data kapal terkait saat mengambil informasi pemilik atau nahkoda. Ketika pengguna meminta data pemilik atau nahkoda melalui API, respons sekarang menyertakan informasi tentang kapal-kapal terkait.

Untuk informasi lebih lanjut tentang dokumentasi API dan integrasi dengan drf-spectacular, lihat [DRF_SPECTACULAR_INTEGRATION.md](DRF_SPECTACULAR_INTEGRATION.md).

## Perubahan yang Dilakukan

### 1. Serializers yang Diperbarui (`owners/serializers.py`)

#### OwnerSerializer

- Menambahkan field `ships` menggunakan `SerializerMethodField` untuk mengambil kapal yang dimiliki oleh pemilik
- Menambahkan field `captains` menggunakan `SerializerMethodField` untuk mengambil nahkoda yang dipekerjakan oleh pemilik
- Mengimplementasikan metode `get_ships()` untuk mengembalikan informasi dasar kapal:
  - ID
  - Nama
  - Nomor registrasi
  - Status aktif
- Mengimplementasikan metode `get_captains()` untuk mengembalikan informasi dasar nahkoda:
  - ID
  - Nama
  - Nomor lisensi

#### CaptainSerializer

- Menambahkan field `ships` menggunakan `SerializerMethodField` untuk mengambil kapal yang dioperasikan oleh nahkoda
- Menambahkan field `owner_name` untuk menampilkan nama pemilik
- Mengimplementasikan metode `get_ships()` untuk mengembalikan informasi dasar kapal:
  - ID
  - Nama
  - Nomor registrasi
  - Status aktif

### 2. Views yang Diperbarui (`owners/views.py`)

#### OwnerViewSet

- Memperbarui queryset untuk menggunakan `prefetch_related('ships', 'captains')` untuk kueri database yang dioptimalkan
- Ini mencegah masalah kueri N+1 saat mengambil data terkait

#### CaptainViewSet

- Menambahkan ViewSet baru untuk mengelola nahkoda
- Memperbarui queryset untuk menggunakan `select_related('owner').prefetch_related('ships')` untuk kueri database yang dioptimalkan
- Menambahkan dekorator dokumentasi drf-spectacular untuk dokumentasi API

### 3. URLs yang Diperbarui (`owners/urls.py`)

- Menambahkan `CaptainViewSet` ke router
- Mendaftarkan endpoint `owners` dan `captains`:
  - `/api/owners/owners/` - Endpoint pemilik
  - `/api/owners/captains/` - Endpoint nahkoda

## Endpoint API

### Endpoint Pemilik

- `GET /api/owners/owners/` - Daftar semua pemilik dengan kapal dan nahkoda terkait
- `POST /api/owners/owners/` - Buat pemilik baru
- `GET /api/owners/owners/{id}/` - Ambil pemilik tertentu dengan kapal dan nahkoda terkait
- `PUT /api/owners/owners/{id}/` - Perbarui pemilik tertentu
- `PATCH /api/owners/owners/{id}/` - Perbarui sebagian pemilik tertentu
- `DELETE /api/owners/owners/{id}/` - Hapus pemilik tertentu

### Endpoint Nahkoda

- `GET /api/owners/captains/` - Daftar semua nahkoda dengan kapal dan pemilik terkait
- `POST /api/owners/captains/` - Buat nahkoda baru
- `GET /api/owners/captains/{id}/` - Ambil nahkoda tertentu dengan kapal dan pemilik terkait
- `PUT /api/owners/captains/{id}/` - Perbarui nahkoda tertentu
- `PATCH /api/owners/captains/{id}/` - Perbarui sebagian nahkoda tertentu
- `DELETE /api/owners/captains/{id}/` - Hapus nahkoda tertentu

## Contoh Struktur Data

### Respons Pemilik

```json
{
  "id": 1,
  "name": "Test Owner",
  "owner_type": "individual",
  "email": "owner@example.com",
  "phone": null,
  "address": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "ships": [
    {
      "id": 1,
      "name": "Test Ship 1",
      "registration_number": "TS123456",
      "active": true
    },
    {
      "id": 2,
      "name": "Test Ship 2",
      "registration_number": "TS789012",
      "active": true
    }
  ],
  "captains": [
    {
      "id": 1,
      "name": "Test Captain",
      "license_number": "CAPT123456"
    }
  ]
}
```

### Respons Nahkoda

```json
{
  "id": 1,
  "name": "Test Captain",
  "license_number": "CAPT123456",
  "owner": 1,
  "user": 1,
  "date_of_birth": null,
  "contact_info": null,
  "email": "captain@example.com",
  "phone": null,
  "address": null,
  "years_of_experience": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "ships": [
    {
      "id": 1,
      "name": "Test Ship 1",
      "registration_number": "TS123456",
      "active": true
    },
    {
      "id": 2,
      "name": "Test Ship 2",
      "registration_number": "TS789012",
      "active": true
    }
  ],
  "owner_name": "Test Owner"
}
```

## Manfaat

1. **Pengurangan Panggilan API**: Klien sekarang dapat mendapatkan informasi lengkap tentang pemilik/nahkoda dan kapal terkait dalam satu permintaan
2. **Peningkatan Kinerja**: Kueri database dioptimalkan menggunakan `select_related()` dan `prefetch_related()`
3. **Pengalaman Pengguna yang Lebih Baik**: Data yang lebih komprehensif dikembalikan tanpa memerlukan permintaan tambahan
4. **Struktur Data yang Konsisten**: Data terkait memiliki struktur yang konsisten di seluruh endpoint

## Catatan Implementasi

1. **Pencegahan Impor Melingkar**: Menggunakan `SerializerMethodField` daripada serializer bersarang untuk menghindari masalah impor melingkar antar aplikasi
2. **Optimasi Kueri**: Mengimplementasikan optimasi kueri database yang tepat untuk mencegah masalah N+1
3. **Kompatibilitas Mundur**: Semua fungsionalitas yang ada tetap tidak berubah
4. **Dokumentasi API**: Menambahkan dokumentasi drf-spectacular yang tepat untuk endpoint baru

## Dokumentasi Tambahan

Untuk informasi lebih lanjut tentang dokumentasi API dan integrasi dengan drf-spectacular, lihat:

- [DRF_SPECTACULAR_INTEGRATION.md](DRF_SPECTACULAR_INTEGRATION.md) - Integrasi dokumentasi dengan drf-spectacular
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Dokumentasi API terperinci
- [README.md](README.md) - Gambaran umum proyek
