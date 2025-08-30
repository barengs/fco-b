# Sistem Manajemen Tangkapan Ikan FCO

Sistem Manajemen Tangkapan Ikan FCO adalah aplikasi berbasis Django REST API yang dirancang untuk membantu pengelolaan laporan tangkapan ikan dari para pemilik kapal. Sistem ini menyediakan cara yang terstruktur dan skalabel untuk mencatat dan mengelola data terkait aktivitas penangkapan ikan, kapal, pemilik, dan spesies.

## Fitur Utama

1. **Pelaporan Tangkapan Ikan**: CRUD (Create, Read, Update, Delete) untuk laporan tangkapan ikan
2. **Manajemen Kapal**: Pendaftaran dan detail kapal penangkap ikan
3. **Manajemen Pemilik**: Manajemen pemilik kapal (perorangan dan perusahaan)
4. **Katalog Spesies Ikan**: Database spesies ikan yang komprehensif
5. **Manajemen Area Penangkapan**: Pengelolaan area dan lokasi penangkapan
6. **Autentikasi Fleksibel**: Login menggunakan username atau nomor registrasi kapal
7. **Import Data**: Import data spesies ikan, ikan individual, kapal, dan area penangkapan dari file CSV
8. **Sistem Peran Pengguna**: Manajemen peran untuk admin KKP, pemilik kapal, dan nahkoda

## Teknologi yang Digunakan

- **Backend**: Django (v4.2.3)
- **API Framework**: Django REST Framework (v3.14.0)
- **Dokumentasi API**: drf-spectacular (Swagger UI dan Redoc)
- **Database**: SQLite (default untuk pengembangan)

## Instalasi

1. **Buat virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Instal dependensi**:

   ```bash
   pip install django djangorestframework drf-spectacular
   ```

3. **Terapkan migrasi database**:

   ```bash
   python manage.py migrate
   ```

4. **Buat pengguna admin**:

   ```bash
   python manage.py createsuperuser
   ```

5. **Jalankan server pengembangan**:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### 1. Modul Owners (Pemilik)

Mengelola pemilik kapal (perorangan dan perusahaan) serta nahkoda

Endpoint:

- `GET /api/owners/owners/` - Daftar semua pemilik
- `POST /api/owners/owners/` - Buat pemilik baru
- `GET /api/owners/owners/{id}/` - Ambil pemilik tertentu
- `PUT /api/owners/owners/{id}/` - Perbarui pemilik
- `PATCH /api/owners/owners/{id}/` - Perbarui sebagian pemilik
- `DELETE /api/owners/owners/{id}/` - Hapus pemilik

- `GET /api/owners/captains/` - Daftar semua nahkoda
- `POST /api/owners/captains/` - Buat nahkoda baru
- `GET /api/owners/captains/{id}/` - Ambil nahkoda tertentu
- `PUT /api/owners/captains/{id}/` - Perbarui nahkoda
- `PATCH /api/owners/captains/{id}/` - Perbarui sebagian nahkoda
- `DELETE /api/owners/captains/{id}/` - Hapus nahkoda
- `POST /api/owners/captains/login/` - Login nahkoda menggunakan nomor registrasi kapal

### 2. Modul Ships (Kapal)

Mengelola kapal penangkap ikan dan atributnya

Endpoint:

- `GET /api/ships/ships/` - Daftar semua kapal
- `POST /api/ships/ships/` - Buat kapal baru
- `GET /api/ships/ships/{id}/` - Ambil kapal tertentu
- `PUT /api/ships/ships/{id}/` - Perbarui kapal
- `PATCH /api/ships/ships/{id}/` - Perbarui sebagian kapal
- `DELETE /api/ships/ships/{id}/` - Hapus kapal
- `GET /api/ships/ships/{id}/catch_reports/` - Dapatkan semua laporan tangkapan untuk kapal tertentu
- `GET /api/ships/check-ship/?registration_number={nomor}` - Periksa apakah nomor registrasi kapal terdaftar
- `POST /api/ships/ships/import_ships/` - Impor kapal dari CSV

### 3. Modul Fish (Ikan)

Mengelola data spesies ikan

Endpoint:

- `GET /api/fish/fish-species/` - Daftar semua spesies ikan
- `POST /api/fish/fish-species/` - Buat spesies ikan baru
- `GET /api/fish/fish-species/{id}/` - Ambil spesies ikan tertentu
- `PUT /api/fish/fish-species/{id}/` - Perbarui spesies ikan
- `PATCH /api/fish/fish-species/{id}/` - Perbarui sebagian spesies ikan
- `DELETE /api/fish/fish-species/{id}/` - Hapus spesies ikan
- `POST /api/fish/fish-species/import_species/` - Impor spesies ikan dari CSV

- `GET /api/fish/fish/` - Daftar semua ikan
- `POST /api/fish/fish/` - Buat ikan baru
- `GET /api/fish/fish/{id}/` - Ambil ikan tertentu
- `PUT /api/fish/fish/{id}/` - Perbarui ikan
- `PATCH /api/fish/fish/{id}/` - Perbarui sebagian ikan
- `DELETE /api/fish/fish/{id}/` - Hapus ikan
- `GET /api/fish/fish/?species_id={id}` - Filter ikan berdasarkan spesies
- `POST /api/fish/fish/import_fish/` - Impor ikan dari CSV

### 4. Modul Catches (Tangkapan)

Mengelola laporan dan detail tangkapan ikan

Endpoint:

- `GET /api/catches/fish-catches/` - Daftar semua laporan tangkapan ikan
- `POST /api/catches/fish-catches/` - Buat laporan tangkapan ikan baru
- `GET /api/catches/fish-catches/{id}/` - Ambil laporan tangkapan ikan tertentu
- `PUT /api/catches/fish-catches/{id}/` - Perbarui laporan tangkapan ikan
- `PATCH /api/catches/fish-catches/{id}/` - Perbarui sebagian laporan tangkapan ikan
- `DELETE /api/catches/fish-catches/{id}/` - Hapus laporan tangkapan ikan

- `GET /api/catches/catch-details/` - Daftar semua detail tangkapan
- `POST /api/catches/catch-details/` - Buat detail tangkapan baru
- `GET /api/catches/catch-details/{id}/` - Ambil detail tangkapan tertentu
- `PUT /api/catches/catch-details/{id}/` - Perbarui detail tangkapan
- `PATCH /api/catches/catch-details/{id}/` - Perbarui sebagian detail tangkapan
- `DELETE /api/catches/catch-details/{id}/` - Hapus detail tangkapan

### 5. Modul Regions (Wilayah)

Mengelola area dan lokasi penangkapan

Endpoint:

- `GET /api/regions/fishing-areas/` - Daftar semua area penangkapan
- `POST /api/regions/fishing-areas/` - Buat area penangkapan baru
- `GET /api/regions/fishing-areas/{id}/` - Ambil area penangkapan tertentu
- `PUT /api/regions/fishing-areas/{id}/` - Perbarui area penangkapan
- `PATCH /api/regions/fishing-areas/{id}/` - Perbarui sebagian area penangkapan
- `DELETE /api/regions/fishing-areas/{id}/` - Hapus area penangkapan
- `POST /api/regions/fishing-areas/import_areas/` - Impor area penangkapan dari CSV

### 6. Modul Admin (Administrasi)

Mengelola peran pengguna, hak akses, dan menu sistem untuk administrator KKP

Endpoint:

- `GET /api/admin/roles/` - Daftar semua peran
- `POST /api/admin/roles/` - Buat peran baru
- `GET /api/admin/roles/{id}/` - Ambil peran tertentu
- `PUT /api/admin/roles/{id}/` - Perbarui peran
- `DELETE /api/admin/roles/{id}/` - Hapus peran

- `GET /api/admin/user-roles/` - Daftar semua penugasan peran pengguna
- `POST /api/admin/user-roles/assign_role/` - Menugaskan peran kepada pengguna

- `GET /api/admin/menus/` - Daftar semua menu aktif
- `POST /api/admin/menus/` - Buat menu baru
- `GET /api/admin/menus/{id}/` - Ambil menu tertentu

- `GET /api/admin/role-menus/` - Daftar semua penugasan menu peran
- `POST /api/admin/role-menus/assign_menu/` - Menugaskan menu kepada peran

## Dokumentasi API Interaktif

Dokumentasi API interaktif tersedia melalui:

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **Redoc**: http://localhost:8000/api/schema/redoc/
- **Schema**: http://localhost:8000/api/schema/

## Autentikasi

Sistem mendukung autentikasi fleksibel yang memungkinkan nahkoda atau pemilik kapal untuk masuk menggunakan:

1. **Username** - Metode tradisional menggunakan username dan password
2. **Nomor Registrasi Kapal** - Metode alternatif menggunakan nomor registrasi kapal dan password

### Endpoint Login

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

### Menggunakan Token untuk Request Berikutnya

Setelah login berhasil, gunakan token dalam header Authorization untuk request berikutnya:

```bash
curl -X GET http://localhost:8000/api/ships/ \
  -H "Authorization: Token your_token_here"
```

Untuk informasi lebih detail tentang implementasi autentikasi, lihat [AUTHENTICATION_FEATURE.md](AUTHENTICATION_FEATURE.md)

## Import Data dari CSV

Sistem mendukung import data dari file CSV untuk beberapa entitas:

### Import Spesies Ikan

Gunakan endpoint `POST /api/fish/fish-species/import_species/` untuk mengimpor data spesies ikan.

Format CSV:

```
name,scientific_name,description
Tuna Sirip Kuning,Thunnus albacares,Tuna dengan sirip kuning yang populer di perairan tropis
Ikan Kakap,Lutjanus campechanus,Ikan laut yang umum ditemukan di perairan hangat
```

### Import Ikan Individual

Gunakan endpoint `POST /api/fish/fish/import_fish/` untuk mengimpor data ikan individual.

Format CSV:

```
species_name,name,length,weight,notes
Tuna Sirip Kuning,Budi,120.5,30.2,Ikan tangkapan pertama
Ikan Kakap,Andi,30.0,2.5,Ikan ukuran sedang
```

### Import Kapal

Gunakan endpoint `POST /api/ships/ships/import_ships/` untuk mengimpor data kapal.

Format CSV:

```
name,registration_number,owner_name,captain_name,length,width,gross_tonnage,year_built,home_port,active
Test Ship 1,SHIP001,Test Owner,Test Captain,20.5,5.2,100.5,2020,Port A,true
Test Ship 2,SHIP002,Test Owner,,15.0,4.0,75.0,2018,Port B,true
```

### Import Area Penangkapan

Gunakan endpoint `POST /api/regions/fishing-areas/import_areas/` untuk mengimpor data area penangkapan.

Format CSV:

```
name,code,description,boundary_coordinates
Area Penangkapan Utara,APU-001,Wilayah penangkapan di utara,"[[10.0, 20.0], [10.5, 20.5]]"
Area Penangkapan Selatan,APS-002,Wilayah penangkapan di selatan,"[[15.0, 25.0], [15.5, 25.5]]"
```

Untuk dokumentasi lengkap tentang endpoint import, lihat:

- [IMPORT_FISH_SPECIES_API.md](IMPORT_FISH_SPECIES_API.md) - Dokumentasi import spesies ikan
- [IMPORT_FISH_API.md](IMPORT_FISH_API.md) - Dokumentasi import ikan individual
- [IMPORT_SHIPS_API.md](IMPORT_SHIPS_API.md) - Dokumentasi import kapal
- [IMPORT_FISHING_AREAS_API.md](IMPORT_FISHING_AREAS_API.md) - Dokumentasi import area penangkapan

## Hubungan Data

Sistem ini memiliki hubungan data yang kompleks dan terintegrasi:

### 1. Owner (Pemilik) ↔ Ship (Kapal)

- **Hubungan**: One-to-Many
- **Deskripsi**: Satu pemilik dapat memiliki banyak kapal, tetapi setiap kapal hanya dimiliki oleh satu pemilik.
- **Field**: `owner` di model Ship

### 2. Ship (Kapal) ↔ Captain (Nahkoda)

- **Hubungan**: One-to-Many
- **Deskripsi**: Satu kapal dapat memiliki banyak nahkoda (selama periode waktu berbeda), tetapi setiap nahkoda hanya dikaitkan dengan satu kapal pada satu waktu.
- **Field**: `ship` di model Captain

### 3. Ship (Kapal) ↔ FishCatch (Tangkapan Ikan)

- **Hubungan**: One-to-Many
- **Deskripsi**: Satu kapal dapat memiliki banyak laporan tangkapan ikan, tetapi setiap laporan tangkapan terkait dengan satu kapal.
- **Field**: `ship` di model FishCatch

### 4. FishCatch (Tangkapan Ikan) ↔ CatchDetail (Detail Tangkapan)

- **Hubungan**: One-to-Many
- **Deskripsi**: Satu laporan tangkapan dapat memiliki banyak detail tangkapan, tetapi setiap detail tangkapan terkait dengan satu laporan.
- **Field**: `fish_catch` di model CatchDetail

### 5. FishSpecies (Spesies Ikan) ↔ Fish (Ikan)

- **Hubungan**: One-to-Many
- **Deskripsi**: Satu spesies ikan dapat memiliki banyak variasi ikan, tetapi setiap ikan terkait dengan satu spesies.
- **Field**: `species` di model Fish

### 6. FishingArea (Area Penangkapan) ↔ FishCatch (Tangkapan Ikan)

- **Hubungan**: Many-to-Many
- **Deskripsi**: Satu area penangkapan dapat digunakan dalam banyak laporan tangkapan, dan satu laporan tangkapan dapat mencakup banyak area penangkapan.
- **Field**: `fishing_areas` di model FishCatch (through relationship)

## Pengujian

Untuk menjalankan pengujian unit:

```bash
python manage.py test
```

## Lisensi

Proyek ini dilisensikan di bawah lisensi MIT - lihat file [LICENSE](LICENSE) untuk detailnya.

## Kontribusi

Kontribusi dipersilakan! Silakan baca [CONTRIBUTING.md](CONTRIBUTING.md) untuk detail tentang proses kontribusi.
