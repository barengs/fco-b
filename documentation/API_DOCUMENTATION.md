# Sistem Manajemen Tangkapan Ikan FCO - Dokumentasi API

## Gambaran Umum

Dokumen ini menyediakan informasi terperinci tentang API Sistem Manajemen Tangkapan Ikan FCO. API dibangun menggunakan Django REST Framework dan didokumentasikan menggunakan drf-spectacular.

Untuk dokumentasi yang lebih komprehensif tentang integrasi drf-spectacular dengan sistem ini, lihat [DRF_SPECTACULAR_INTEGRATION.md](DRF_SPECTACULAR_INTEGRATION.md).

## URL Dasar

```
http://localhost:8000/api/
```

## Autentikasi

API menggunakan sistem autentikasi bawaan Django. Beberapa endpoint dilindungi dan memerlukan autentikasi.

## Endpoint API

### 1. Modul Fish (Ikan)

#### Spesies Ikan

- `GET /fish/fish-species/` - Daftar semua spesies ikan
- `POST /fish/fish-species/` - Buat spesies ikan baru
- `GET /fish/fish-species/{id}/` - Ambil spesies ikan tertentu
- `PUT /fish/fish-species/{id}/` - Perbarui spesies ikan
- `PATCH /fish/fish-species/{id}/` - Perbarui sebagian spesies ikan
- `DELETE /fish/fish-species/{id}/` - Hapus spesies ikan
- `POST /fish/fish-species/import_species/` - Impor spesies ikan dari CSV

#### Ikan

- `GET /fish/fish/` - Daftar semua ikan
- `POST /fish/fish/` - Buat ikan baru
- `GET /fish/fish/{id}/` - Ambil ikan tertentu
- `PUT /fish/fish/{id}/` - Perbarui ikan
- `PATCH /fish/fish/{id}/` - Perbarui sebagian ikan
- `DELETE /fish/fish/{id}/` - Hapus ikan
- `GET /fish/fish/?species_id={id}` - Filter ikan berdasarkan spesies
- `POST /fish/fish/import_fish/` - Impor ikan dari CSV

### 2. Modul Owners (Pemilik)

#### Pemilik

- `GET /owners/owners/` - Daftar semua pemilik
- `POST /owners/owners/` - Buat pemilik baru
- `GET /owners/owners/{id}/` - Ambil pemilik tertentu
- `PUT /owners/owners/{id}/` - Perbarui pemilik
- `PATCH /owners/owners/{id}/` - Perbarui sebagian pemilik
- `DELETE /owners/owners/{id}/` - Hapus pemilik

#### Nahkoda

- `GET /owners/captains/` - Daftar semua nahkoda
- `POST /owners/captains/` - Buat nahkoda baru
- `GET /owners/captains/{id}/` - Ambil nahkoda tertentu
- `PUT /owners/captains/{id}/` - Perbarui nahkoda
- `PATCH /owners/captains/{id}/` - Perbarui sebagian nahkoda
- `DELETE /owners/captains/{id}/` - Hapus nahkoda
- `POST /owners/captains/login/` - Login nahkoda menggunakan nomor registrasi kapal

### 3. Modul Ships (Kapal)

Mengelola kapal penangkap ikan dan atributnya

Endpoint:

- `GET /ships/ships/` - Daftar semua kapal
- `POST /ships/ships/` - Buat kapal baru
- `GET /ships/ships/{id}/` - Ambil kapal tertentu
- `PUT /ships/ships/{id}/` - Perbarui kapal
- `PATCH /ships/ships/{id}/` - Perbarui sebagian kapal
- `DELETE /ships/ships/{id}/` - Hapus kapal
- `GET /ships/ships/{id}/catch_reports/` - Dapatkan semua laporan tangkapan untuk kapal tertentu
- `GET /ships/check-ship/?registration_number={nomor}` - Periksa apakah nomor registrasi kapal terdaftar
- `POST /ships/ships/import_ships/` - Impor kapal dari CSV

### 4. Modul Catches (Tangkapan)

Mengelola laporan dan detail tangkapan ikan

Endpoint:

- `GET /catches/fish-catches/` - Daftar semua laporan tangkapan ikan
- `POST /catches/fish-catches/` - Buat laporan tangkapan ikan baru
- `GET /catches/fish-catches/{id}/` - Ambil laporan tangkapan ikan tertentu
- `PUT /catches/fish-catches/{id}/` - Perbarui laporan tangkapan ikan
- `PATCH /catches/fish-catches/{id}/` - Perbarui sebagian laporan tangkapan ikan
- `DELETE /catches/fish-catches/{id}/` - Hapus laporan tangkapan ikan

- `GET /catches/catch-details/` - Daftar semua detail tangkapan
- `POST /catches/catch-details/` - Buat detail tangkapan baru
- `GET /catches/catch-details/{id}/` - Ambil detail tangkapan tertentu
- `PUT /catches/catch-details/{id}/` - Perbarui detail tangkapan
- `PATCH /catches/catch-details/{id}/` - Perbarui sebagian detail tangkapan
- `DELETE /catches/catch-details/{id}/` - Hapus detail tangkapan

### 5. Modul Regions (Wilayah)

Mengelola area dan lokasi penangkapan

Endpoint:

- `GET /regions/fishing-areas/` - Daftar semua area penangkapan
- `POST /regions/fishing-areas/` - Buat area penangkapan baru
- `GET /regions/fishing-areas/{id}/` - Ambil area penangkapan tertentu
- `PUT /regions/fishing-areas/{id}/` - Perbarui area penangkapan
- `PATCH /regions/fishing-areas/{id}/` - Perbarui sebagian area penangkapan
- `DELETE /regions/fishing-areas/{id}/` - Hapus area penangkapan
- `POST /regions/fishing-areas/import_areas/` - Impor area penangkapan dari CSV

### 6. Modul Admin (Administrasi)

Mengelola peran pengguna, hak akses, dan menu sistem untuk administrator KKP

Endpoint:

- `GET /admin/roles/` - Daftar semua peran
- `POST /admin/roles/` - Buat peran baru
- `GET /admin/roles/{id}/` - Ambil peran tertentu
- `PUT /admin/roles/{id}/` - Perbarui peran
- `DELETE /admin/roles/{id}/` - Hapus peran

- `GET /admin/user-roles/` - Daftar semua penugasan peran pengguna
- `POST /admin/user-roles/assign_role/` - Menugaskan peran kepada pengguna

- `GET /admin/menus/` - Daftar semua menu aktif
- `POST /admin/menus/` - Buat menu baru
- `GET /admin/menus/{id}/` - Ambil menu tertentu

- `GET /admin/role-menus/` - Daftar semua penugasan menu peran
- `POST /admin/role-menus/assign_menu/` - Menugaskan menu kepada peran

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

## Model Data

### FishSpecies (Spesies Ikan)

- `name` (string, unik) - Nama spesies ikan
- `scientific_name` (string, opsional) - Nama ilmiah spesies
- `description` (text, opsional) - Deskripsi spesies
- `created_at` (datetime) - Timestamp pembuatan
- `updated_at` (datetime) - Timestamp pembaruan terakhir

### Fish (Ikan)

- `species` (foreign key ke FishSpecies) - Spesies ikan
- `name` (string, opsional) - Nama ikan
- `length` (decimal, opsional) - Panjang ikan dalam cm
- `weight` (decimal, opsional) - Berat ikan dalam kg
- `notes` (text, opsional) - Catatan tambahan
- `created_at` (datetime) - Timestamp pembuatan
- `updated_at` (datetime) - Timestamp pembaruan terakhir

### Owner (Pemilik)

- `name` (string) - Nama pemilik
- `owner_type` (string) - Tipe pemilik (individual atau company)
- `contact_info` (text, opsional) - Informasi kontak
- `email` (email, opsional) - Email pemilik
- `phone` (string, opsional) - Nomor telepon
- `address` (text, opsional) - Alamat pemilik
- `created_at` (datetime) - Timestamp pembuatan
- `updated_at` (datetime) - Timestamp pembaruan terakhir

### Ship (Kapal)

- `name` (string) - Nama kapal
- `registration_number` (string, unik) - Nomor registrasi kapal
- `owner` (foreign key ke Owner) - Pemilik kapal
- `captain` (foreign key ke Captain, opsional) - Nahkoda kapal
- `length` (decimal, opsional) - Panjang kapal dalam meter
- `width` (decimal, opsional) - Lebar kapal dalam meter
- `gross_tonnage` (decimal, opsional) - Tonase kotor kapal
- `year_built` (integer, opsional) - Tahun pembuatan kapal
- `home_port` (string, opsional) - Pelabuhan asal kapal
- `active` (boolean) - Status aktif kapal
- `created_at` (datetime) - Timestamp pembuatan
- `updated_at` (datetime) - Timestamp pembaruan terakhir

### Captain (Nahkoda)

- `name` (string) - Nama nahkoda
- `license_number` (string, unik) - Nomor lisensi nahkoda
- `owner` (foreign key ke Owner) - Pemilik kapal
- `user` (foreign key ke CustomUser, opsional) - Akun pengguna
- `date_of_birth` (date, opsional) - Tanggal lahir
- `contact_info` (text, opsional) - Informasi kontak
- `email` (email, opsional) - Email
- `phone` (string, opsional) - Nomor telepon
- `address` (text, opsional) - Alamat
- `years_of_experience` (integer, opsional) - Tahun pengalaman
- `created_at` (datetime) - Timestamp pembuatan
- `updated_at` (datetime) - Timestamp pembaruan terakhir

### FishCatch (Tangkapan Ikan)

- `ship` (foreign key ke Ship) - Kapal yang melakukan tangkapan
- `catch_date` (date) - Tanggal tangkapan
- `total_weight` (decimal) - Berat total tangkapan dalam kg
- `total_value` (decimal, opsional) - Nilai total tangkapan
- `fishing_areas` (many-to-many ke FishingArea) - Area penangkapan
- `notes` (text, opsional) - Catatan tambahan
- `created_at` (datetime) - Timestamp pembuatan
- `updated_at` (datetime) - Timestamp pembaruan terakhir

### CatchDetail (Detail Tangkapan)

- `fish_catch` (foreign key ke FishCatch) - Laporan tangkapan yang terkait
- `species` (foreign key ke FishSpecies) - Spesies ikan yang ditangkap
- `quantity` (integer) - Jumlah ikan
- `weight` (decimal) - Berat ikan dalam kg
- `value` (decimal, opsional) - Nilai tangkapan
- `notes` (text, opsional) - Catatan tambahan
- `created_at` (datetime) - Timestamp pembuatan
- `updated_at` (datetime) - Timestamp pembaruan terakhir

### FishingArea (Area Penangkapan)

- `name` (string) - Nama area penangkapan
- `code` (string, unik) - Kode area penangkapan
- `description` (text, opsional) - Deskripsi area
- `boundary_coordinates` (text, opsional) - Koordinat batas area (format JSON atau teks)
- `created_at` (datetime) - Timestamp pembuatan
- `updated_at` (datetime) - Timestamp pembaruan terakhir

## Endpoint Import Data

### Import Spesies Ikan

**Endpoint**: `POST /fish/fish-species/import_species/`

**Deskripsi**: Mengimpor data spesies ikan dari format CSV

**Parameter**:

- `csv_data` (string, required): Data CSV dengan header: name,scientific_name,description
- `clear_existing` (boolean, optional, default: false): Jika true, hapus semua spesies ikan yang ada sebelum mengimpor

**Contoh CSV**:

```
name,scientific_name,description
Tuna Sirip Kuning,Thunnus albacares,Tuna dengan sirip kuning yang populer di perairan tropis
Ikan Kakap,Lutjanus campechanus,Ikan laut yang umum ditemukan di perairan hangat
```

### Import Ikan

**Endpoint**: `POST /fish/fish/import_fish/`

**Deskripsi**: Mengimpor data ikan individual dari format CSV

**Parameter**:

- `csv_data` (string, required): Data CSV dengan header: species_name,name,length,weight,notes
- `clear_existing` (boolean, optional, default: false): Jika true, hapus semua ikan yang ada sebelum mengimpor

**Contoh CSV**:

```
species_name,name,length,weight,notes
Tuna Sirip Kuning,Budi,120.5,30.2,Ikan tangkapan pertama
Ikan Kakap,Andi,30.0,2.5,Ikan ukuran sedang
```

### Import Kapal

**Endpoint**: `POST /ships/ships/import_ships/`

**Deskripsi**: Mengimpor data kapal dari format CSV

**Parameter**:

- `csv_data` (string, required): Data CSV dengan header: name,registration_number,owner_name,captain_name,length,width,gross_tonnage,year_built,home_port,active
- `clear_existing` (boolean, optional, default: false): Jika true, hapus semua kapal yang ada sebelum mengimpor

**Contoh CSV**:

```
name,registration_number,owner_name,captain_name,length,width,gross_tonnage,year_built,home_port,active
Test Ship 1,SHIP001,Test Owner,Test Captain,20.5,5.2,100.5,2020,Port A,true
Test Ship 2,SHIP002,Test Owner,,15.0,4.0,75.0,2018,Port B,true
```

### Import Area Penangkapan

**Endpoint**: `POST /regions/fishing-areas/import_areas/`

**Deskripsi**: Mengimpor data area penangkapan dari format CSV

**Parameter**:

- `csv_data` (string, required): Data CSV dengan header: name,code,description,boundary_coordinates
- `clear_existing` (boolean, optional, default: false): Jika true, hapus semua area penangkapan yang ada sebelum mengimpor

**Contoh CSV**:

```
name,code,description,boundary_coordinates
Area Penangkapan Utara,APU-001,Wilayah penangkapan di utara,"[[10.0, 20.0], [10.5, 20.5]]"
Area Penangkapan Selatan,APS-002,Wilayah penangkapan di selatan,"[[15.0, 25.0], [15.5, 25.5]]"
```
