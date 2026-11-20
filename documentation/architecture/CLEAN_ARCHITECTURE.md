# Panduan Arsitektur Bersih (Clean Architecture) Backend FishPro (`fco-b`)

Dokumen ini menjelaskan penerapan prinsip **Clean Architecture** pada backend Django REST Framework `fco-b`, pemisahan lapisan tanggung jawab (*Separation of Concerns*), penataan direktori, serta pemecahan modul monolit menjadi komponen yang siap untuk pemeliharaan jangka panjang (*enterprise-grade maintenance*).

---

## 1. Penataan Struktur Direktori Root Proyek

Sebelumnya, berbagai script pengujian, data sampel CSV/JSON, dan file dokumentasi berserakan di direktori utama (*root project*). Struktur tersebut kini dirapikan menjadi:

```
fco-b/
├── data/
│   └── samples/                # Data sampel CSV & JSON historis (bukan di root)
│       ├── catch_data_36_months.csv
│       ├── sample_catch_data.csv
│       ├── template.csv
│       ├── pnbp_history.json
│       ├── pnbp_predictions.json
│       └── test_pnbp_predictions.json
├── documentation/              # Dokumentasi teknis & API terpadu
│   ├── CLEAN_ARCHITECTURE.md
│   ├── DOKUMENTASI_API.md
│   ├── SUPER_ADMIN_GUIDE.md
│   ├── LSTM_EPOCH_CHANGES.md
│   └── ...
├── scripts/                    # Script pemeliharaan & pengujian standalone
│   ├── activate_superuser.py
│   ├── check_superuser.py
│   ├── create_superadmin.py
│   ├── create_test_quotas.py
│   ├── verify_superadmin.py
│   ├── test_iot_scale.py
│   ├── test_pnbp.py
│   ├── fco2.py
│   └── fix_db.sh
├── manage.py                   # Django CLI entry point
├── Dockerfile                  # Containerization
├── requirements.txt            # Dependensi Python
└── fco_project/                # Pengaturan utama Django & routing pusat
```

---

## 2. Pemisahan Lapisan Clean Architecture

Setiap modul/aplikasi pada `fco-b` mengadopsi 4 lapisan Clean Architecture yang saling terisolasi dengan arah dependensi ke dalam (*Inward Dependency Rule*):

```
       +-------------------------------------------------------+
       |                  Presentation Layer                   |
       |  (DRF ViewSets, API Views, Serializers, Permissions)  |
       +---------------------------+---------------------------+
                                   |
                                   v
       +-------------------------------------------------------+
       |                  Application Layer                    |
       |      (Use Cases, Business Services, Workflows)        |
       +---------------------------+---------------------------+
                                   |
                                   v
       +-------------------------------------------------------+
       |                     Domain Layer                      |
       |    (Entities, Value Objects, Policies, Calculations)  |
       +-------------------------------------------------------+
                                   ^
                                   |
       +---------------------------+---------------------------+
       |                 Infrastructure Layer                  |
       |    (ML Models, Blockchain Miner, SSE Bus, File I/O)   |
       +-------------------------------------------------------+
```

### A. Domain Layer (`domain/`)
* **Tanggung Jawab**: Menyimpan aturan bisnis murni (*core business logic*) yang tidak boleh bergantung pada Django framework, database, atau antarmuka HTTP.
* **Implementasi**:
  * `ships/domain/quota_policy.py`: Logika ambang batas kuota (*Kritis* $< 15\%$, *Waspada* $< 35\%$, *Aman* $\ge 35\%$), rasio pemakaian kuota, dan kepatuhan.
  * `ships/domain/exceptions.py`: Eksepsi domain seperti `QuotaExceededException`, `InvalidVesselRegistrationException`.
  * `catches/domain/pnbp_rules.py`: Formula deterministik perhitungan PNBP sesuai PP No. 85 Tahun 2021 ($\text{Volume} \times \text{HPI} \times \text{Tarif}$).
  * `blockchain/domain/block_entity.py`: Aturan kriptografi blok, kalkulasi SHA-256 payload, dan validasi Proof-of-Work.

### B. Application Layer (`application/`)
* **Tanggung Jawab**: Mengatur orkestrasi alur kerja use-case bisnis, memvalidasi masukan sebelum diproses domain, dan menghubungkan infrastruktur.
* **Implementasi**:
  * `ships/application/ship_csv_service.py`: Use-case ekspor template CSV dan *ingestion parsing* data kapal massal (memotong ratusan baris kode dari `ships/views.py`).

### C. Infrastructure Layer (`infrastructure/`)
* **Tanggung Jawab**: Berinteraksi dengan teknologi eksternal, komputasi numerik, perangkat keras, dan pustaka data science.
* **Implementasi**:
  * `ships/infrastructure/ml/`:
    * `lstm_network.py`: Jaringan saraf tiruan LSTM dari nol dengan NumPy (Forward & Backward pass).
    * `lstm_predictor.py`: Normalisasi MinMaxScaler, sliding window 6 bulan, autoregressive rollout 12 bulan, dan early stopping.
    * `nsga3_optimizer.py`: Algoritma genetika multiobjektif Platypus dengan 4 fungsi objektif dan seleksi kompromi Pareto.
    * `data_generator.py`: Agregasi data historis dan sintesis baseline musiman monsun maritim.
    * `dual_stage.py`: Orkestrator sekuensial Dual-Stage (LSTM $\rightarrow$ NSGA-III).
  * `catches/infrastructure/pnbp_predictor.py`: Model peramalan ensemble 4-metode (Regresi Multivariat, MLP Neural Network, NSGA-III, ARIMA).
  * `iot_scales/infrastructure/event_bus.py`: In-memory thread-safe `ScaleEventBus` untuk penyiaran telemetri timbangan via Server-Sent Events (SSE).

### D. Presentation Layer (`presentation/` / `views/` / `serializers/`)
* **Tanggung Jawab**: Delivery mechanism perantara klien HTTP (peramban web / mobile). Memvalidasi payload JSON dan mengatur kode status HTTP.
* **Implementasi**:
  * `ships/presentation/permissions.py`: Class `IsShipOwnerOrAdmin` untuk proteksi Anti-IDOR.
  * `catches/presentation/permissions.py`: Class `IsCatchOwnerOrAdmin` untuk proteksi manipulasi laporan tangkapan.
  * `catches/views.py` & `ships/views.py`: Facade controllers yang menyajikan ViewSets resmi DRF.

---

## 3. Hasil Refactoring & Pengurangan Kompleksitas File

| File Monolit Awal | Baris Awal | Setelah Refactoring | Pengurangan | Komponen yang Dipisahkan |
| :--- | :--- | :--- | :--- | :--- |
| **`ships/views.py`** | 1.532 baris | **600 baris** | **-60.8%** | 520 baris duplikasi tak sengaja dibersihkan; logika impor CSV dipindah ke `ShipCsvService`; izin ke `permissions.py`. |
| **`ships/ml_models.py`** | 674 baris | **23 baris** (Facade) | **-96.6%** | Dipecah menjadi 5 modul terisolasi di `ships/infrastructure/ml/`. |
| **`catches/views.py`** | 1.225 baris | **878 baris** | **-28.3%** | Logika predictor ensemble AI (356 baris) dipindah ke `catches/infrastructure/pnbp_predictor.py`. |
| **Root Directory** | 18 file liar | **0 file liar** | **100% rapi** | Script dipindah ke `scripts/`, data ke `data/samples/`, panduan ke `documentation/`. |

---

## 4. Jaminan Kompatibilitas Mundur (Zero Breaking Changes)

Seluruh URL endpoints, Django management commands, dan import eksternal tetap bekerja 100% tanpa perubahan rute API melalui teknik **Facade Re-exporting**:
* `from ships.ml_models import LSTMNetwork, DualStageQuotaOptimizer` $\rightarrow$ Tetap berfungsi normal.
* `from catches.views import PNBPredictor` $\rightarrow$ Tetap berfungsi normal.
* `GET /api/ships/ships/`, `POST /api/catches/fish-catches/`, `GET /api/catches/charts/unified/` $\rightarrow$ Tetap stabil dengan respons identik.
