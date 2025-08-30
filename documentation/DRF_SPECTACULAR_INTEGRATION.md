# Integrasi Dokumentasi FCO dengan drf-spectacular

## Gambaran Umum

Dokumen ini menjelaskan bagaimana semua dokumentasi dalam proyek Sistem Manajemen Tangkapan Ikan FCO telah terintegrasi dengan sistem dokumentasi drf-spectacular untuk menyediakan dokumentasi API interaktif yang komprehensif.

## Komponen Dokumentasi

### 1. Dokumentasi API Interaktif (drf-spectacular)

Dokumentasi API interaktif dihasilkan secara otomatis menggunakan drf-spectacular dan dapat diakses melalui:

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **Redoc**: http://localhost:8000/api/schema/redoc/
- **Schema**: http://localhost:8000/api/schema/

### 2. Dokumentasi Statis

Dokumentasi statis yang melengkapi dokumentasi interaktif:

- **README.md**: Gambaran umum proyek dan instruksi penggunaan
- **API_DOCUMENTATION.md**: Dokumentasi API terperinci dengan deskripsi endpoint dan model data
- **MODEL_RELATIONSHIPS.md**: Diagram hubungan model dan penjelasan relasi
- **SERIALIZER_IMPLEMENTATION.md**: Implementasi serializer dengan data terkait

## Integrasi drf-spectacular dengan ViewSets

### Modul Owners

#### OwnerViewSet

Dekorator `@extend_schema_view` diterapkan dengan deskripsi dalam bahasa Indonesia:

- `list`: Daftar semua pemilik
- `create`: Buat pemilik baru
- `retrieve`: Ambil pemilik tertentu
- `update`: Perbarui pemilik
- `partial_update`: Perbarui sebagian pemilik
- `destroy`: Hapus pemilik

#### CaptainViewSet

Dekorator `@extend_schema_view` diterapkan dengan deskripsi dalam bahasa Indonesia:

- `list`: Daftar semua nahkoda
- `create`: Buat nahkoda baru
- `retrieve`: Ambil nahkoda tertentu
- `update`: Perbarui nahkoda
- `partial_update`: Perbarui sebagian nahkoda
- `destroy`: Hapus nahkoda

### Modul Ships

#### ShipViewSet

Dekorator `@extend_schema_view` diterapkan dengan deskripsi dalam bahasa Indonesia:

- `list`: Daftar semua kapal
- `create`: Buat kapal baru
- `retrieve`: Ambil kapal tertentu
- `update`: Perbarui kapal
- `partial_update`: Perbarui sebagian kapal
- `destroy`: Hapus kapal
- `catch_reports`: Dapatkan laporan tangkapan kapal (aksi kustom)

### Modul Fish

#### FishSpeciesViewSet

Dekorator `@extend_schema_view` diterapkan dengan deskripsi dalam bahasa Indonesia:

- `list`: Daftar semua spesies ikan
- `create`: Buat spesies ikan baru
- `retrieve`: Ambil spesies ikan tertentu
- `update`: Perbarui spesies ikan
- `partial_update`: Perbarui sebagian spesies ikan
- `destroy`: Hapus spesies ikan

#### FishViewSet

Dekorator `@extend_schema_view` diterapkan dengan deskripsi dalam bahasa Indonesia:

- `list`: Daftar semua ikan
- `create`: Buat ikan baru
- `retrieve`: Ambil ikan tertentu
- `update`: Perbarui ikan
- `partial_update`: Perbarui sebagian ikan
- `destroy`: Hapus ikan

### Modul Catches

#### FishCatchViewSet

Dekorator `@extend_schema_view` diterapkan dengan deskripsi dalam bahasa Indonesia:

- `list`: Daftar semua laporan tangkapan ikan
- `create`: Buat laporan tangkapan ikan baru
- `retrieve`: Ambil laporan tangkapan ikan tertentu
- `update`: Perbarui laporan tangkapan ikan
- `partial_update`: Perbarui sebagian laporan tangkapan ikan
- `destroy`: Hapus laporan tangkapan ikan

#### CatchDetailViewSet

Dekorator `@extend_schema_view` diterapkan dengan deskripsi dalam bahasa Indonesia:

- `list`: Daftar semua detail tangkapan
- `create`: Buat detail tangkapan baru
- `retrieve`: Ambil detail tangkapan tertentu
- `update`: Perbarui detail tangkapan
- `partial_update`: Perbarui sebagian detail tangkapan
- `destroy`: Hapus detail tangkapan

### Modul Regions

#### FishingAreaViewSet

Dekorator `@extend_schema_view` diterapkan dengan deskripsi dalam bahasa Indonesia:

- `list`: Daftar semua area penangkapan
- `create`: Buat area penangkapan baru
- `retrieve`: Ambil area penangkapan tertentu
- `update`: Perbarui area penangkapan
- `partial_update`: Perbarui sebagian area penangkapan
- `destroy`: Hapus area penangkapan

## Fitur Dokumentasi Interaktif

### 1. Pengujian API Langsung

- Swagger UI dan Redoc menyediakan antarmuka untuk menguji endpoint API secara langsung
- Otentikasi dapat diuji melalui interface yang disediakan

### 2. Deskripsi Endpoint Terperinci

- Setiap endpoint menyertakan ringkasan dan deskripsi komprehensif dalam bahasa Indonesia
- Parameter, body request, dan response dijelaskan secara detail

### 3. Dokumentasi Model Data

- Semua model data dan field mereka didokumentasikan secara otomatis
- Hubungan antar model ditampilkan dengan jelas

### 4. Informasi Autentikasi

- Persyaratan autentikasi untuk setiap endpoint dijelaskan
- Panduan untuk berbagai metode autentikasi

### 5. Penanganan Kesalahan

- Dokumentasi respon kesalahan standar HTTP
- Kode status dan pesan kesalahan yang umum

## Cara Mengakses Dokumentasi

### 1. Menjalankan Server Pengembangan

```bash
python manage.py runserver
```

### 2. Mengakses Dokumentasi Interaktif

Setelah server berjalan, akses salah satu dari:

- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- Redoc: http://localhost:8000/api/schema/redoc/

### 3. Mengakses Dokumentasi Statis

Dokumentasi statis dapat dilihat langsung dalam file:

- README.md
- API_DOCUMENTATION.md
- MODEL_RELATIONSHIPS.md
- SERIALIZER_IMPLEMENTATION.md

## Manfaat Integrasi

### 1. Dokumentasi yang Selalu Terkini

- Dokumentasi interaktif dihasilkan secara otomatis dari kode
- Perubahan pada API secara otomatis tercermin dalam dokumentasi

### 2. Pengalaman Pengembang yang Lebih Baik

- Kombinasi dokumentasi statis dan interaktif memberikan pemahaman komprehensif
- Pengujian API langsung mempercepat proses pengembangan

### 3. Konsistensi Bahasa

- Semua dokumentasi menggunakan bahasa Indonesia untuk konsistensi
- Istilah teknis dalam bahasa Inggris dipertahankan sesuai standar industri

### 4. Aksesibilitas

- Berbagai format dokumentasi memenuhi kebutuhan berbeda
- Dokumentasi interaktif memudahkan eksplorasi API

## Penggunaan Dokumentasi

### Untuk Pengembang Backend

1. Gunakan dokumentasi interaktif untuk memahami struktur API
2. Referensikan dokumentasi statis untuk pemahaman konsep yang lebih dalam
3. Gunakan Swagger UI/Redoc untuk menguji endpoint selama pengembangan

### Untuk Pengembang Frontend

1. Gunakan dokumentasi interaktif untuk memahami endpoint yang tersedia
2. Referensikan dokumentasi model data untuk memahami struktur respons
3. Gunakan dokumentasi untuk mengimplementasikan integrasi API

### Untuk Administrator Sistem

1. Gunakan dokumentasi untuk memahami struktur data dan hubungan antar entitas
2. Referensikan dokumentasi instalasi untuk deployment

## Pemeliharaan Dokumentasi

### 1. Memperbarui Dokumentasi ViewSet

Saat menambahkan atau memodifikasi endpoint:

- Tambahkan dekorator `@extend_schema_view` dengan deskripsi dalam bahasa Indonesia
- Pastikan semua operasi (list, create, retrieve, update, partial_update, destroy) didokumentasikan

### 2. Memperbarui Dokumentasi Statis

Saat ada perubahan signifikan pada sistem:

- Perbarui README.md dengan informasi terbaru
- Sesuaikan API_DOCUMENTATION.md dengan perubahan endpoint
- Perbarui diagram dan penjelasan dalam MODEL_RELATIONSHIPS.md

### 3. Memastikan Konsistensi Bahasa

- Semua dokumentasi baru harus menggunakan bahasa Indonesia
- Pertahankan istilah teknis dalam bahasa Inggris sesuai standar industri

## Kesimpulan

Integrasi dokumentasi FCO dengan drf-spectacular berhasil menciptakan sistem dokumentasi yang komprehensif dan interaktif. Kombinasi dokumentasi statis dan dinamis memberikan pengalaman terbaik bagi semua pengguna sistem, sementara pemeliharaan otomatis memastikan dokumentasi tetap akurat seiring perkembangan sistem.
