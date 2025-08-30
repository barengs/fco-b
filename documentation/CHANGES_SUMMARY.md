# Ringkasan Perubahan - Relasi Kapal, Pemilik, dan Nahkoda

## Perubahan yang Dilakukan

### 1. Model Ship (ships/models.py)

- **Penambahan field `captain`**:
  - Tipe: `ForeignKey` ke model `Captain`
  - Relationship: One-to-Many (satu nahkoda dapat mengoperasikan banyak kapal)
  - `on_delete`: `SET_NULL` (jika nahkoda dihapus, kapal tetap ada tapi field captain menjadi null)
  - `null`: `True` (kapal bisa tidak memiliki nahkoda)
  - `blank`: `True` (field tidak wajib diisi)
  - `related_name`: `'ships'` (untuk akses reverse dari Captain ke Ship)

### 2. Model Captain (owners/models.py)

- **Perbaikan referensi `user`**:
  - Mengubah referensi `'CustomUser'` (string) menjadi `CustomUser` (objek langsung)
  - Memperbaiki error "Related model 'owners.customuser' cannot be resolved"

### 3. Admin Interface (ships/admin.py)

- **Penambahan field `captain`** di `list_display`
- **Penambahan field `captain`** di `list_filter`

### 4. Serializer (ships/serializers.py)

- **Penambahan field `captain_name`** untuk menampilkan nama nahkoda

### 5. ViewSet (ships/views.py)

- **Optimasi query** dengan `select_related('owner', 'captain')` untuk menghindari N+1 query problem

### 6. Migrations

- **0002_ship_captain.py**: Migration untuk menambahkan field captain ke model Ship
- **Perbaikan migration** untuk model Captain

## Hubungan Data yang Terbentuk

### Struktur Relasi

```
Owner (1) ───< Ship (N)
Owner (1) ───< Captain (N)
Captain (1) ───< Ship (N)
```

### Penjelasan Relasi

1. **Owner → Ship**: Satu pemilik dapat memiliki banyak kapal
2. **Owner → Captain**: Satu pemilik dapat mempekerjakan banyak nahkoda
3. **Captain → Ship**: Satu nahkoda dapat mengoperasikan banyak kapal

## Pengujian

### Test Script (test_relationships.py)

Membuat script pengujian yang memverifikasi:

1. Pembuatan owner, captain, user, dan ship berhasil
2. Relasi ship → owner berfungsi dengan benar
3. Relasi ship → captain berfungsi dengan benar
4. Relasi captain → owner berfungsi dengan benar
5. Relasi reverse owner → ships berfungsi dengan benar
6. Relasi reverse captain → ships berfungsi dengan benar
7. Relasi reverse owner → captains berfungsi dengan benar

### Hasil Pengujian

```
Testing relationships...
Created owner: Test Owner
Created user: testcaptain
Created captain: Captain Test
Created ship: Test Ship

Testing relationships:
Ship owner: Test Owner
Ship captain: Captain Test
Captain owner: Test Owner
Owner ships count: 1
Captain ships count: 1

Testing reverse relationships:
First ship of owner: Test Ship
First ship of captain: Test Ship
First captain of owner: Captain Test

All relationships working correctly!
```

## Dokumentasi

### README.md

- Menambahkan penjelasan tentang hubungan data dalam Fitur Utama
- Menambahkan penjelasan tentang modul Owners yang sekarang mencakup nahkoda
- Menambahkan bagian "Hubungan Data" yang menjelaskan semua relasi dalam sistem

### MODEL_RELATIONSHIPS.md

- Membuat diagram ER untuk memvisualisasikan hubungan antar model
- Memberikan penjelasan detail untuk setiap hubungan
- Menyertakan field-field penting dalam setiap model

## Manfaat Perubahan

### 1. Integritas Data

- Hubungan antar entitas lebih jelas dan terstruktur
- Data dapat diakses secara konsisten dari berbagai arah

### 2. Efisiensi Query

- Penggunaan `select_related()` mengurangi jumlah query database
- Akses ke data terkait tidak memerlukan query tambahan

### 3. Kemudahan Pengembangan

- Struktur data yang jelas memudahkan pengembangan fitur baru
- Relasi yang lengkap memungkinkan analisis data yang lebih kompleks

### 4. User Experience

- Data kapal sekarang menampilkan informasi lengkap tentang pemilik dan nahkoda
- Filter berdasarkan nahkoda memudahkan pencarian data

## Kompatibilitas

Perubahan ini:

- Tidak merusak data yang sudah ada
- Tidak mengubah API endpoint yang sudah ada
- Menambahkan fungsionalitas baru tanpa mengganggu yang lama
- Mengikuti pola desain yang konsisten dengan bagian lain dari sistem
