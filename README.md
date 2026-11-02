# FishPro Backend (`fco-b`) — Sistem API & Layanan Inti Perikanan Terpadu

FishPro Backend (`fco-b` / *Fisheries Catch Organization Backend*) adalah pusat layanan berbasis **Django REST Framework (DRF)** yang mengorkestrasi seluruh data transaksi penangkapan ikan, regulasi kepatuhan kuota, telemetri timbangan pelabuhan (IoT), rantai blok kriptografis (*blockchain immutability*), serta model kecerdasan buatan (*AI/ML*) perikanan nasional.

---

## Daftar Isi
1. [Latar Belakang & Tujuan Folder `fco-b`](#1-latar-belakang--tujuan-folder-fco-b)
2. [Alasan Pemisahan dari Struktur Proyek Utama (`fishpro`)](#2-alasan-pemisahan-dari-struktur-proyek-utama-fishpro)
3. [Arsitektur Sistem: Clean Architecture 4 Lapisan](#3-arsitektur-sistem-clean-architecture-4-lapisan)
4. [Struktur Direktori & Pemetaan Modul](#4-struktur-direktori--pemetaan-modul)
5. [Dokumentasi Lengkap API Endpoints & Fitur Terbaru](#5-dokumentasi-lengkap-api-endpoints--fitur-terbaru)
6. [Subsistem Kecerdasan Buatan (AI/ML Engines)](#6-subsistem-kecerdasan-buatan-aiml-engines)
7. [Subsistem IoT Timbangan Pintar & Event Bus Realtime](#7-subsistem-iot-timbangan-pintar--event-bus-realtime)
8. [Subsistem Audit Blockchain](#8-subsistem-audit-blockchain)
9. [Konfigurasi Lingkungan (Environment Variables)](#9-konfigurasi-lingkungan-environment-variables)
10. [Panduan Instalasi & Menjalankan Aplikasi](#10-panduan-instalasi--menjalankan-aplikasi)
11. [Verifikasi Kualitas & Pengujian (Testing)](#11-verifikasi-kualitas--pengujian-testing)
12. [Panduan Kontribusi & Standar Rekayasa Kode](#12-panduan-kontribusi--standar-rekayasa-kode)

---

## 1. Latar Belakang & Tujuan Folder `fco-b`

Folder `fco-b` bertindak sebagai **Single Source of Truth (SSOT)** untuk ekosistem platform perikanan FishPro. Tujuan utama modul backend ini mencakup:
* **Pencatatan Transaksi Tangkapan Resmi**: Menyimpan data tangkapan ikan dari kapal nelayan dan armada industri dengan verifikasi nomor registrasi kapal, nahkoda berlisensi, dan area tangkap WPP.
* **Otomasi Regulasi PNBP & PNKP**: Menghitung secara otomatis kewajiban Penerimaan Negara Bukan Pajak (PNBP) dan Pungutan Hasil Perikanan (PNKP) berdasarkan Peraturan Pemerintah No. 85 Tahun 2021 dan Kepmen KP yang berlaku.
* **Pengawasan Kepatuhan Kuota (Quota Enforcement)**: Mencegah penangkapan ikan berlebih (*overfishing*) dengan pemotongan kuota real-time dan klasifikasi risiko kuota kapal (*Aman*, *Waspada*, *Kritis*).
* **Integrasi Penimbangan Dermaga (IoT)**: Menghubungkan load cell timbangan digital di pelabuhan secara langsung ke server untuk eliminasi kesalahan input manual.
* **Keabsahan Data Kriptografis (Blockchain)**: Menghasilkan jejak audit digital yang tidak dapat diubah (*immutable ledger*) untuk mencegah pemalsuan laporan hasil laut.
* **Peramalan & Alokasi Kuota Berkelanjutan**: Memberikan rekomendasi alokasi kuota berbasis data historis dan daya dukung lingkungan (*Maximum Sustainable Yield*).

---

## 2. Alasan Pemisahan dari Struktur Proyek Utama (`fishpro`)

Repositori FishPro mengadopsi struktur monorepo modular di mana backend (`fco-b`) dan frontend web (`fishpro`) dipisahkan ke dalam folder mandiri pada level root `/modular/fco/`. Alasan utama pemisahan ini:

### A. Pemisahan Tanggung Jawab (*Separation of Concerns*)
* `fco-b` berfokus pada logika domain, keamanan autentikasi multi-peran, integritas basis data, kalkulasi numerik AI, dan pipeline IO file berukuran besar.
* `fishpro` berfokus pada visualisasi antarmuka pengguna, komponen interaktif, pemetaan peta spasial WPP, dan penanganan status frontend berbasis React, Vite, dan Tailwind CSS.

### B. Arsitektur Multi-Klien (*Multi-Client Ingestion Architecture*)
Backend `fco-b` dirancang sebagai API terbuka terpusat yang melayani beragam agen dan klien secara simultan:
1. **Frontend Web Dashboard (`fishpro`)**: Dashboard analitik untuk Admin KKP, Pengawas/Regulator, Pemilik Kapal (*Owner*), dan Nahkoda.
2. **Perangkat Edge IoT Timbangan Pelabuhan**: Mikrokontroler / gateway timbangan mengirim telemetri berat via HTTP POST langsung ke `/api/iot/receive-weight/`.
3. **Aplikasi Mobile (Nelayan & Nahkoda)**: Aplikasi genggam di laut yang beroperasi dengan payload JSON ringan dan autentikasi token.
4. **Sistem Terintegrasi Eksternal**: Pertukaran data dengan kementerian atau otoritas pelabuhan perikanan.

### C. Isolasi Lingkungan Eksekusi & Dependensi Runtime
* Backend berjalan di lingkungan **Python 3.10–3.12** dengan dependensi komputasi numerik berat (`numpy`, `scikit-learn`, `platypus-opt`, `statsmodels`, `whitenoise`, `psycopg2`).
* Frontend berjalan di lingkungan **Node.js 20+** dengan bundler Vite dan library ekosistem JavaScript.
* Pemisahan folder memastikan dependensi tidak saling mengotori, mempermudah kontainerisasi Docker terpisah, serta mempercepat pipeline CI/CD independen.

### D. Skalabilitas & Manajemen Sumber Daya Independen
Komputasi kalkulasi LSTM/NSGA-III dan streaming Server-Sent Events (SSE) membutuhkan profil CPU dan memori yang berbeda dari penyajian aset statis frontend. Backend dapat di-deploy pada VM/container berperforma tinggi atau dihubungkan ke cluster PostgreSQL independen.

---

## 3. Arsitektur Sistem: Clean Architecture 4 Lapisan

Sesuai refactoring bertahap sejak commit `de9caf68`, `fco-b` menerapkan prinsip **Clean Architecture** (Robert C. Martin) dengan **Inward Dependency Rule** (ketergantungan selalu mengarah ke dalam):

```
       +-------------------------------------------------------+
       |                  Presentation Layer                   |
       |     (ViewSets, API Views, Serializers, Permissions)   |
       +---------------------------+---------------------------+
                                   |
                                   v
       +-------------------------------------------------------+
       |                  Application Layer                    |
       |       (Use-Cases, Service Facades, Orchestration)     |
       +---------------------------+---------------------------+
                                   |
                                   v
       +-------------------------------------------------------+
       |                     Domain Layer                      |
       |     (Entities, Value Objects, Domain Validations)     |
       +-------------------------------------------------------+
                                   ^
                                   |
       +---------------------------+---------------------------+
       |                 Infrastructure Layer                  |
       |      (ML Engines, Blockchain Miner, SSE Event Bus)    |
       +-------------------------------------------------------+
```

### Rincian Tanggung Jawab Lapisan:
1. **Domain Layer (`domain/`)**:
   Menyimpan entitas bisnis murni, kalkulasi deterministik, ambang batas kepatuhan, dan validasi data. Lapisan ini bebas dari dependensi Django framework maupun pustaka HTTP.
   *Contoh:* `ships/domain/quota_policy.py`, `catches/domain/pnbp_rules.py`, `iot_scales/domain/iot_device_domain.py`.
2. **Application Layer (`application/`)**:
   Mengorkestrasikan alur kerja use-case bisnis, menghubungkan domain dengan akses data, serta menangani transaksi atomik.
   *Contoh:* `ships/application/ship_csv_service.py`, `catches/application/pnbp_service.py`, `iot_scales/application/iot_device_service.py`, `owners/application/owner_service.py`.
3. **Infrastructure Layer (`infrastructure/`)**:
   Menangani teknologi eksternal, komputasi sains data, kriptografi, dan komunikasi real-time.
   *Contoh:* `ships/infrastructure/ml/` (jaringan LSTM & algoritma NSGA-III), `catches/infrastructure/pnbp_predictor.py`, `iot_scales/infrastructure/event_bus.py`.
4. **Presentation Layer (`presentation/`, `views.py`, `serializers.py`)**:
   Menangani protokol komunikasi HTTP, autentikasi request, otorisasi Anti-IDOR, serialisasi JSON, dan dokumentasi OpenAPI. Root `views.py` bertindak sebagai facade controller tipis.

---

## 4. Struktur Direktori & Pemetaan Modul

```
fco-b/
├── fco_project/                # Pengaturan utama proyek Django
│   ├── settings.py             # Konfigurasi database, CORS, JWT/Token, SPECTACULAR
│   ├── urls.py                 # Master routing tabel endpoint
│   ├── wsgi.py / asgi.py       # WSGI/ASGI entry point
│   └── templates/              # Template kustom Swagger/Redoc
│
├── authentication/             # Modul Autentikasi Pengguna & Token
│   ├── domain/                 # Role mapping & User profile entities
│   ├── application/            # AuthApplicationService (login, register, logout)
│   ├── infrastructure/         # TokenService (DRF AuthToken & lifecycle)
│   ├── serializers.py          # Serializer registrasi & login
│   ├── urls.py                 # Rute: /api/auth/
│   └── views.py                # Presentation ViewSet
│
├── catches/                    # Modul Laporan Tangkapan & Analitik PNBP
│   ├── domain/                 # Aturan perhitungan PNBP & PNKP (PP 85/2021)
│   ├── application/            # CatchApplicationService, PNBPredictionService
│   ├── infrastructure/         # PNBPredictor (Regresi, MLP, NSGA-III, ARIMA)
│   ├── presentation/           # Permissions Anti-IDOR & PNBP Views
│   ├── dashboard_views.py      # Agregasi Dashboard Admin, Regulator, Owner, Captain
│   ├── dashboard_urls.py       # Rute: /api/dashboard/
│   ├── urls.py                 # Rute: /api/catches/
│   └── views.py                # Facade ViewSets & CSV Ingestion
│
├── ships/                      # Modul Kapal, Nahkoda, & Alokasi Kuota
│   ├── domain/                 # Quota policy, ambang batas, eksepsi bisnis
│   ├── application/            # ShipCsvService (ekspor/impor massal kapal)
│   ├── infrastructure/ml/      # Dual-Stage AI (LSTM Network + NSGA-III Optimizer)
│   ├── presentation/views/     # ShipViewSet, QuotaEndpoints, RecommendationViews
│   ├── ml_models.py            # Facade kompatibilitas mundur untuk model ML
│   ├── urls.py                 # Rute: /api/ships/
│   └── views.py                # Facade ViewSet armada
│
├── iot_scales/                 # Modul Timbangan Cerdas IoT Dermaga
│   ├── domain/                 # SmartScaleDomain, ScaleReadingDomain
│   ├── application/            # SmartScaleApplicationService (timbang & simpan)
│   ├── infrastructure/         # ScaleEventBus (Thread-safe SSE in-memory pub/sub)
│   ├── urls.py                 # Rute: /api/iot/
│   └── views.py                # Endpoint ingestion berat, live SSE, & konversi tangkapan
│
├── blockchain/                 # Modul Audit Kriptografi & Imutabilitas
│   ├── domain/                 # BlockEntity, BlockchainDomainService (PoW & hashing)
│   ├── application/            # BlockchainApplicationService (status & verifikasi)
│   ├── infrastructure/         # Blockchain Infrastructure
│   ├── utils.py                # Genesis block builder & transaction sealer
│   ├── urls.py                 # Rute: /api/blockchain/
│   └── views.py                # Endpoint status, transaksi, & blok
│
├── owners/                     # Modul Pemilik Kapal & Lisensi Nahkoda
│   ├── domain/                 # OwnerDomain, OwnerDomainService
│   ├── application/            # OwnerApplicationService (filter queryset & profil)
│   ├── urls.py                 # Rute: /api/owners/
│   └── views.py                # ViewSet pemilik & nahkoda
│
├── regions/                    # Modul Wilayah Pengelolaan Perikanan (WPP)
│   ├── domain/                 # RegionDomain, format kode WPP
│   ├── application/            # RegionApplicationService (CSV ingestion)
│   ├── urls.py                 # Rute: /api/regions/
│   └── views.py                # ViewSet WPP
│
├── fish/                       # Modul Katalog Spesies & Spesimen Ikan
│   ├── domain/                 # FishSpeciesDomain, FishDomain
│   ├── application/            # FishSpeciesApplicationService, FishApplicationService
│   ├── urls.py                 # Rute: /api/fish/
│   └── views.py                # ViewSet katalog spesies & sampel ikan
│
├── admin_module/               # Modul Tata Kelola RBAC & Hierarki Pengguna
│   ├── models.py               # Role, Permission, UserRole, Menu, RoleMenu, AdminProfile
│   ├── urls.py                 # Rute: /api/admin/
│   └── views.py                # Manajemen RBAC & registrasi regulator
│
├── scripts/                    # Skrip Utilitas Standalone & Maintenance
│   ├── create_superadmin.py    # Pembuat akun superadmin otomatis
│   ├── create_test_quotas.py   # Seeder kuota kapal tahun aktif
│   ├── test_iot_scale.py       # Simulator pengirim data berat mikrokontroler
│   ├── test_pnbp.py            # Tester kalkulasi prediksi PNBP
│   └── verify_superadmin.py    # Verifikasi hak akses superadmin
│
├── data/samples/               # Berkas Sampel Dataset & Template CSV
│   ├── catch_data_36_months.csv# Data historis 3 tahun untuk training AI
│   ├── sample_catch_data.csv   # Contoh format data tangkapan
│   └── template.csv            # Berkas master template import
│
└── documentation/              # Dokumentasi Teknis Terperinci
    ├── CLEAN_ARCHITECTURE.md   # Panduan refactor Clean Architecture
    ├── DOKUMENTASI_API.md      # Rincian spesifikasi kontrak API
    └── SUPER_ADMIN_GUIDE.md    # Panduan operasional Super Administrator
```

---

## 5. Dokumentasi Lengkap API Endpoints & Fitur Terbaru

Semua endpoint berbasis REST menggunakan prefix URL `/api/`. Autentikasi menggunakan header standar:  
`Authorization: Token <token_anda>`

### A. Autentikasi Pengguna & Reset Password (`/api/auth/`)
Sistem mendukung autentikasi ganda (Username standar atau Nomor Registrasi Kapal untuk nahkoda/pemilik) serta alur pemulihan kata sandi bertahap (wizard):
* `POST /api/auth/login/` — Login dengan `username` atau `registration_number` + `password`. Mengembalikan token, refresh token, profil lengkap, role (`superadmin`, `admin`, `regulator`, `owner`, `captain`), dan izin menu.
* `POST /api/auth/register/` — Registrasi mandiri akun baru dengan opsi penautan langsung ke profil kapal/pemilik.
* `POST /api/auth/refresh/` — Memperbarui token autentikasi kedaluwarsa menggunakan refresh token valid.
* `POST /api/auth/logout/` — Menghapus token autentikasi aktif dan mencabut refresh token pengguna.
* `POST /api/auth/reset-password/request/` — Minta kode OTP 6 digit pemulihan kata sandi (Step 1 Reset Wizard: menerima email akun atau nomor registrasi kapal).
* `POST /api/auth/reset-password/verify/` — Verifikasi keabsahan kode OTP 6 digit (Step 2 Reset Wizard).
* `POST /api/auth/reset-password/confirm/` — Menetapkan kata sandi baru minimal 8 karakter (Step 3 Reset Wizard).
* `POST /api/auth/reset-password/` — Endpoint langsung untuk reset kata sandi dalam satu request.

### B. Dashboard Terpadu Berbasis Peran (`/api/dashboard/`)
Menyediakan agregasi KPI dan analitik instan tanpa komputasi berulang di sisi frontend:
* `GET /api/dashboard/admin/` — KPI nasional (total kapal, pemilik, volume tangkap kg, estimasi PNBP), deret waktu grafik bulanan aktual & prediksi AI, sebaran WPP, top 5 kapal kuota kritis, dan status blockchain. *(Akses: Admin & Superadmin)*
* `GET /api/dashboard/regulator/` — Total armada diawasi, radar kepatuhan kuota, jumlah kapal kategori waspada/kritis, status timbangan IoT aktif, dan audit blockchain. *(Akses: Regulator & Admin)*
* `GET /api/dashboard/owner/` — KPI armada milik pengguna, sisa kuota rata-rata kapal, total tagihan PNBP berjalan, daftar status operasional kapal dan nahkoda. *(Akses: Owner & Admin)*
* `GET /api/dashboard/captain/` — Spesifikasi teknis kapal yang dinahkodai, kuota tahun aktif (terpakai vs tersisa), 5 riwayat tangkapan tersegel terakhir. *(Akses: Captain & Admin)*

### C. Manajemen Kapal & Kuota AI (`/api/ships/`)
* `GET /api/ships/ships/` — Daftar seluruh kapal (mendukung filter `owner_id`, `captain_id`, dan pencarian).
* `POST /api/ships/ships/` — Registrasi kapal baru (nama, nomor registrasi, GT, dimensi, izin).
* `GET /api/ships/ships/{id}/` — Detail data kapal beserta riwayat kuota tahun berjalan.
* `GET /api/ships/ships/download_template/` — Unduh template CSV resmi untuk import massal armada kapal.
* `POST /api/ships/ships/import_ships/` — Impor massal data kapal via CSV (otomatis membuat pemilik/nahkoda jika belum terdaftar).
* `GET /api/ships/check-ship/?registration_number={no}` — Pemeriksaan cepat status validasi nomor registrasi kapal.
* `GET /api/ships/ai-recommendations/` — Rekomendasi armada berkinerja terbaik berbasis evaluasi produktivitas historis.
* `POST /api/ships/predict-quota/` — Prediksi kuota bulanan kapal berbasis kombinasi model LSTM & NSGA-III.
* `POST /api/ships/regulator/manual-quota/` — Alokasi atau penyesuaian kuota manual tahunan oleh regulator.

### D. Laporan Tangkapan & Analitik PNBP (`/api/catches/`)
* `GET /api/catches/fish-catches/` — Daftar laporan tangkapan (mendukung filter tanggal dan kapal).
* `POST /api/catches/fish-catches/` — Buat laporan tangkapan baru.
* `GET /api/catches/fish-catches-with-details/` — Ambil data laporan tangkapan lengkap bersama rincian spesies, berat, dan kalkulasi PNBP.
* `POST /api/catches/fish-catches-with-details/` — Kirim satu tangkapan beserta detail multi-spesies sekaligus dalam satu transaksi atomik.
* `GET /api/catches/fish-catches/download_template/` — Unduh template CSV impor tangkapan ikan.
* `POST /api/catches/fish-catches/import_csv/` — Impor data tangkapan massal dari CSV (mendukung mode dry-run).
* `POST /api/catches/pnbp/predict/` — Jalankan pipeline prediksi PNBP masa depan (4 metode ensemble).
* `GET /api/catches/pnbp/history/` — Ambil data time-series historis penerimaan PNBP dari database.
* `GET /api/catches/pnbp/latest-predictions/` — Dapatkan hasil ramalan PNBP terbaru yang tersimpan.
* `GET /api/catches/charts/unified/` — Endpoint grafik tunggal yang menyatukan data tren historis, proyeksi PNBP masa depan, dan perbandingan kuota kapal.

### E. IoT Timbangan Cerdas & Live SSE Stream (`/api/iot/`)
* `GET /api/iot/devices/` — CRUD manajemen perangkat timbangan pintar di pelabuhan.
* `POST /api/iot/receive-weight/` — Endpoint penerima data berat dari mikrokontroler/gateway IoT. Mendukung autentikasi token perangkat (`X-Device-Token`) dan langsung menyiarkan event ke bus frontend.
* `GET /api/iot/stream/?device_id={id}` — **Server-Sent Events (SSE)** endpoint. Frontend membuka koneksi stream untuk menerima pembacaan timbangan secara realtime per detik tanpa perlu polling berulang.
* `GET /api/iot/latest/?device_id={id}&status=pending` — Ambil pembacaan berat terkini yang belum diproses untuk auto-fill di form penimbangan.
* `GET /api/iot/readings/` — Log riwayat pembacaan berat timbangan digital.
* `POST /api/iot/save-catch/` — Simpan tangkapan resmi berdasarkan hasil timbang: memvalidasi sisa kuota kapal, membuat record tangkapan, menghitung otomatis tarif PNBP, menandai status timbang menjadi `saved`, dan menyegel data ke blockchain.

### F. Integritas Data & Rantai Blok (`/api/blockchain/`)
* `GET /api/blockchain/status/` — Memeriksa validitas matematis seluruh rantai blok (*chain integrity check*) dan total blok/transaksi.
* `GET /api/blockchain/blocks/` — Mengambil daftar blok dalam rantai (termasuk index, timestamp, hash, previous_hash, data payload, dan nonce Proof-of-Work).
* `GET /api/blockchain/transactions/` — Daftar riwayat transaksi tangkapan yang telah disegel ke dalam rantai blok.

### G. Master Data Wilayah & Spesies Ikan
* `/api/regions/fishing-areas/` — CRUD Wilayah Pengelolaan Perikanan (WPPNRI 571 s.d. 718).
* `/api/regions/fishing-areas/download_template/` — Unduh template CSV/Excel master WPP.
* `/api/regions/fishing-areas/import_areas/` — Impor data wilayah perikanan dari CSV.
* `/api/fish/fish-species/` — CRUD database katalog spesies ikan (nama umum, nama latin, deskripsi).
* `/api/fish/fish-species/download_template/` — Unduh template CSV spesies ikan.
* `/api/fish/fish-species/import_species/` — Impor master data spesies ikan dari CSV.

### H. Tata Kelola Hak Akses Administrasi (`/api/admin/`)
* `/api/admin/roles/` — Manajemen peran sistem (*Role-Based Access Control*).
* `/api/admin/menus/` & `/api/admin/role-menus/` — Konfigurasi dinamis hak akses menu navigasi frontend per peran.
* `/api/admin/admin-users/` — Manajemen profil staf administrator.
* `POST /api/admin/admin-users/register_regulator/` — Registrasi akun petugas pengawas/regulator pelabuhan baru oleh admin.

### I. Skema & Dokumentasi Interaktif
* `GET /api/schema/` — OpenAPI 3.0 YAML/JSON Schema generation via `drf-spectacular`.
* `GET /api/docs/` — Swagger UI interaktif untuk simulasi dan pengujian langsung seluruh endpoint dari browser.
* `GET /api/docs/redoc/` — Antarmuka dokumentasi alternatif Redoc.

---

## 6. Subsistem Kecerdasan Buatan (AI/ML Engines)

FishPro Backend mengimplementasikan arsitektur AI hibrida dua tahap (**Dual-Stage AI Framework**) untuk menyelesaikan konflik klasik antara produktivitas ekonomi armada dan kelestarian ekologis perikanan:

### Tahap 1: Prediksi Time-Series LSTM (*Predictive Stage*)
* Dibangun secara native menggunakan komputasi matriks `numpy` di `ships/infrastructure/ml/lstm_network.py`.
* Menerapkan normalisasi `MinMaxScaler`, sliding window observasi 6 bulan, dan autoregressive rollout 12 bulan ke depan.
* Menangkap fluktuasi non-linear seperti siklus monsun maritim dan musim puncak penangkapan (*peak catch season*).

### Tahap 2: Optimasi Multi-Objektif NSGA-III (*Prescriptive Stage*)
* Menggunakan algoritma genetika multiobjektif *Non-dominated Sorting Genetic Algorithm III* (Platypus).
* Mengoptimalkan 4 fungsi objektif simultan:
  1. **Maksimasi Pendapatan**: Nilai ekonomi tangkapan dan PNBP negara.
  2. **Kelestarian Sumber Daya (*Sustainability*)**: Menjaga batas daya dukung lingkungan (*Maximum Sustainable Yield*).
  3. **Kepatuhan Kuota (*Quota Fidelity*)**: Menghindari deviasi ekstrem dari alokasi kuota regulasi.
  4. **Pemerataan Sosial (*Social Equity*)**: Distribusi kuota berkeadilan antara armada kapal skala kecil (<30 GT) dan industri (>30 GT).

### Ensemble 4-Metode Peramalan PNBP
Diimplementasikan di `catches/infrastructure/pnbp_predictor.py` untuk menghasilkan angka prediksi PNBP yang robust:
$$\text{PNBP}_{\text{final}} = 0.25 \times \text{Regresi} + 0.35 \times \text{Neural Network (MLP)} + 0.25 \times \text{NSGA-III} + 0.15 \times \text{ARIMA}$$

---

## 7. Subsistem IoT Timbangan Pintar & Event Bus Realtime

Untuk menjamin kecepatan komunikasi di dermaga tanpa memberatkan basis data:
* **In-Memory Thread-Safe Event Bus**: Menggunakan queue per-koneksi di `iot_scales/infrastructure/event_bus.py`.
* **Zero-Latency Ingestion**: Begitu mikrokontroler menimbang ikan dan mengirim payload HTTP ke backend, data langsung dipublikasikan ke kanal SSE pelanggan yang terhubung (`/api/iot/stream/`).
* **Heartbeat & Resiliensi Proxy**: Dilengkapi mekanisme ping keep-alive berkala untuk mencegah pemutusan koneksi otomatis oleh reverse proxy (Nginx/Cloudflare).

---

## 8. Subsistem Audit Blockchain

* **Struktur Blok**: Setiap blok menyimpan `index`, `timestamp`, `previous_hash`, `hash`, `nonce`, dan payload data transaksi tangkapan dalam format JSON kanonikal.
* **Algoritma Konsensus**: Proof-of-Work (PoW) sederhana berbasis SHA-256 dengan tingkat kesulitan dinamis (*difficulty target*).
* **Verifikasi Integritas Otomatis**: Layanan `BlockchainApplicationService.verify_chain()` memverifikasi keutuhan rantai blok dari blok genesis hingga blok mutakhir secara otomatis saat diakses oleh regulator.

---

## 9. Konfigurasi Lingkungan (Environment Variables)

Salin berkas template lingkungan sebelum menjalankan server:
```bash
cp .env.example .env
```

### Variabel Lingkungan yang Didukung:
| Variabel | Tipe | Nilai Default | Keterangan |
| :--- | :--- | :--- | :--- |
| `DEBUG` | Boolean | `True` | Mode debug Django (`True` / `False`). |
| `SECRET_KEY` | String | `django-insecure-...` | Kunci enkripsi sesi dan token Django. |
| `ALLOWED_HOSTS` | Comma-separated | `*` | Daftar host/domain yang diizinkan (contoh: `api.fishpro.id,localhost`). |
| `USE_SQLITE` | Boolean | `False` | Jika `True`, backend menggunakan database file SQLite lokal (`db.sqlite3`). |
| `DB_NAME` / `POSTGRES_DB` | String | `fishpro` | Nama basis data PostgreSQL. |
| `DB_USER` / `POSTGRES_USER` | String | `fishpro` | Nama pengguna basis data. |
| `DB_PASSWORD` / `POSTGRES_PASSWORD` | String | `fishpro` | Kata sandi pengguna basis data. |
| `DB_HOST` / `POSTGRES_HOST` | String | `localhost` | Alamat host PostgreSQL. |
| `DB_PORT` / `POSTGRES_PORT` | Integer | `5432` | Port layanan PostgreSQL. |

---

## 10. Panduan Instalasi & Menjalankan Aplikasi

### A. Persiapan Lingkungan Virtual
Pastikan Python 3.10, 3.11, atau 3.12 telah terpasang di sistem operasi Anda:

```bash
# Masuk ke direktori fco-b
cd /home/makdumibrohim/Projects/Web-Dev/modular/fco/fco-b

# Buat virtual environment
python3 -m venv .venv

# Aktifkan virtual environment
source .venv/bin/activate  # Di Linux/macOS
# .venv\Scripts\activate   # Di Windows
```

### B. Pemasangan Dependensi
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### C. Eksekusi Migrasi Basis Data
```bash
# Menggunakan SQLite untuk pengembangan lokal:
USE_SQLITE=1 python manage.py migrate

# Atau menggunakan PostgreSQL sesuai konfigurasi .env:
python manage.py migrate
```

### D. Pembuatan Akun Administrator & Data Awal
Tersedia skrip otomasi pada folder `scripts/` untuk inisialisasi cepat:

```bash
# 1. Buat akun superadministrator default
USE_SQLITE=1 python scripts/create_superadmin.py

# 2. Buat data sampel kuota kapal untuk simulasi
USE_SQLITE=1 python scripts/create_test_quotas.py
```

### E. Menjalankan Server Pengembangan
```bash
USE_SQLITE=1 python manage.py runserver 0.0.0.0:8000
```
Server API aktif pada `http://localhost:8000/`. Dokumentasi Swagger otomatis dapat diakses di `http://localhost:8000/api/docs/`.

---

## 11. Verifikasi Kualitas & Pengujian (Testing)

Sebelum melakukan commit atau deployment, jalankan serangkaian uji kepatuhan berikut:

### 1. Eksekusi Seluruh Unit Test (Test Suite)
Memastikan keabsahan autentikasi, impor file, proteksi Anti-IDOR, dan kalkulasi:
```bash
USE_SQLITE=1 python manage.py test --verbosity=1
```
*(Seluruh 30/30 unit test harus berstatus `OK` tanpa failure maupun error).*

### 2. Validasi Integritas Sistem Django
```bash
USE_SQLITE=1 python manage.py check
```
*(Harus melaporkan: `System check identified no issues (0 silenced)`).*

### 3. Validasi Kompilasi Skema OpenAPI
Memastikan generator skema `drf-spectacular` tidak menemui kendala pada serializer:
```bash
USE_SQLITE=1 python manage.py spectacular --file /tmp/schema.json
```

---

## 12. Panduan Kontribusi & Standar Rekayasa Kode

Bagi kontributor yang menambahkan endpoint atau fitur baru ke `fco-b`:

1. **Patuhi Arah Ketergantungan Clean Architecture**:
   - Aturan bisnis deterministik **wajib** ditempatkan di `domain/`.
   - Logika alur use-case, transaksi, dan interaksi antar model **wajib** dikemas di `application/*_service.py`.
   - Presentation layer (`views.py`) hanya bertugas menerima payload, memanggil serializer, mendelegasikan ke application service, dan mengembalikan respons HTTP.
2. **Pertahankan Kompatibilitas Mundur (Backward Compatibility)**:
   - Jangan mengubah struktur path URL atau kunci respons JSON yang telah dikonsumsi oleh frontend `fishpro`.
   - Bila memecah modul lama, pertahankan fungsi/class lama sebagai facade di file induk.
3. **Dokumentasikan dengan Decorator `@extend_schema`**:
   - Setiap view atau action DRF baru harus dianotasi dengan `@extend_schema(tags=[...], summary=...)` agar muncul rapi pada dokumentasi Swagger.
4. **Validasi Mandiri**:
   - Pastikan kode baru tidak memicu peringatan linter dan sertakan test case pendukung di modul `tests/`.
