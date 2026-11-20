# FCO Backend (fco-b) Technical Documentation

Selamat datang di indeks dokumentasi teknis sistem backend **Fish Catch Official (FCO)** berbasis Django REST Framework. Seluruh dokumen telah dikelompokkan secara terstruktur ke dalam sub-kategori berikut:

---

## 📑 Daftar Isi Dokumentasi

### 1. 🌐 API & Integrasi (`documentation/api/`)
Dokumentasi spesifikasi endpoint REST API, schema, template impor, dan integrasi pengujian Postman:
- [API_DOCUMENTATION.md](api/API_DOCUMENTATION.md): Dokumentasi menyeluruh endpoint API backend.
- [DOKUMENTASI_API.md](api/DOKUMENTASI_API.md): Panduan integrasi API berbahasa Indonesia.
- [COMBINED_ENDPOINT.md](api/COMBINED_ENDPOINT.md): Spesifikasi endpoint gabungan pelaporan tangkapan.
- [ADMIN_USERS_ENDPOINT.md](api/ADMIN_USERS_ENDPOINT.md): Endpoint manajemen akun pengguna dan petugas.
- [DRF_SPECTACULAR_INTEGRATION.md](api/DRF_SPECTACULAR_INTEGRATION.md): Integrasi OpenAPI 3.0 / Swagger UI.
- [IOT_SMART_SCALE_API.md](api/IOT_SMART_SCALE_API.md): Endpoint & WebSocket timbangan pintar IoT.
- [QUOTA_PREDICTION_API.md](api/QUOTA_PREDICTION_API.md): Endpoint prediksi kuota tangkapan berbasis ML/AI.
- [POSTMAN_TESTING_DOCUMENTATION.md](api/POSTMAN_TESTING_DOCUMENTATION.md): Koleksi dan panduan pengujian Postman terpadu.
- [PNBP_PREDICTION_POSTMAN_DOCUMENTATION.md](api/PNBP_PREDICTION_POSTMAN_DOCUMENTATION.md): Pengujian Postman untuk prediksi PNBP.
- [IMPORT_FISHING_AREAS_API.md](api/IMPORT_FISHING_AREAS_API.md): API impor data wilayah penangkapan (WPP).
- [IMPORT_FISH_API.md](api/IMPORT_FISH_API.md): API impor master data ikan.
- [IMPORT_FISH_SPECIES_API.md](api/IMPORT_FISH_SPECIES_API.md): API impor master spesies ikan.
- [IMPORT_SHIPS_API.md](api/IMPORT_SHIPS_API.md): API impor master data kapal nelayan.
- [IMPORT_SHIPS_TEMPLATE.md](api/IMPORT_SHIPS_TEMPLATE.md): Format template spreadsheet impor kapal.

---

### 2. ✨ Modul & Fitur Spesifik (`documentation/features/`)
Panduan teknis dan implementasi fitur spesifik per domain bisnis:
- [ADMIN_MODULE_DOCUMENTATION.md](features/ADMIN_MODULE_DOCUMENTATION.md): Modul administrasi master data dan sistem.
- [ADMIN_MODULE_SUMMARY.md](features/ADMIN_MODULE_SUMMARY.md): Ringkasan fitur dan arsitektur modul admin.
- [AUTHENTICATION_FEATURE.md](features/AUTHENTICATION_FEATURE.md): Alur autentikasi token JWT dan otorisasi peran.
- [AUTH_ENDPOINTS_SUMMARY.md](features/AUTH_ENDPOINTS_SUMMARY.md): Ringkasan rute endpoint autentikasi.
- [BLOCKCHAIN_MODULE.md](features/BLOCKCHAIN_MODULE.md): Arsitektur buku besar terdesentralisasi (blockchain ledger).
- [BLOCKCHAIN_DEMO.md](features/BLOCKCHAIN_DEMO.md): Panduan verifikasi dan demo hashing rantai blok.
- [BLOCKCHAIN_FEATURE_SUMMARY.md](features/BLOCKCHAIN_FEATURE_SUMMARY.md): Ringkasan audit dan integritas data tangkapan.
- [LOGIN_PROFILE_FEATURE.md](features/LOGIN_PROFILE_FEATURE.md): Respons profil saat login pengguna.
- [REFRESH_TOKEN_FEATURE.md](features/REFRESH_TOKEN_FEATURE.md): Mekanisme rotasi dan pembaruan refresh token.
- [REGISTRATION_PROFILE_FEATURE.md](features/REGISTRATION_PROFILE_FEATURE.md): Penautan profil pengguna saat registrasi.
- [REGISTRATION_ROLE_FEATURE.md](features/REGISTRATION_ROLE_FEATURE.md): Pemilihan peran (Captain/Owner) saat pendaftaran.
- [ROLE_SYSTEM_DOCUMENTATION.md](features/ROLE_SYSTEM_DOCUMENTATION.md): Sistem RBAC (Role-Based Access Control).
- [USER_AS_FIELD_FEATURE.md](features/USER_AS_FIELD_FEATURE.md): Relasi user dengan entitas pemilik dan nahkoda.
- [SHIP_LINKING.md](features/SHIP_LINKING.md): Mekanisme penautan nahkoda dan pemilik ke armada kapal.
- [SHIP_REGISTRATION_CHECK.md](features/SHIP_REGISTRATION_CHECK.md): Validasi nomor izin dan registrasi kapal.
- [QUOTA_PREDICTION_SUMMARY.md](features/QUOTA_PREDICTION_SUMMARY.md): Ringkasan modul kuota & optimasi NSGA-III.
- [LSTM_EPOCH_CHANGES.md](features/LSTM_EPOCH_CHANGES.md): Kalibrasi epoch model prediksi LSTM.
- [REGIONS_MODULE.md](features/REGIONS_MODULE.md): Dokumentasi modul wilayah laut WPPNRI.
- [SUPER_ADMIN_GUIDE.md](features/SUPER_ADMIN_GUIDE.md): Panduan inisialisasi dan akses Super Administrator.

---

### 3. 🏗️ Arsitektur, Model & Database (`documentation/architecture/`)
Struktur data, relasi tabel, pola arsitektur, dan riwayat migrasi database:
- [CLEAN_ARCHITECTURE.md](architecture/CLEAN_ARCHITECTURE.md): Panduan arsitektur berlapis Domain, Application, & Infrastructure.
- [MODEL_RELATIONSHIPS.md](architecture/MODEL_RELATIONSHIPS.md): Diagram dan relasi antar-model database.
- [app_structure.md](architecture/app_structure.md): Pemetaan hirarki dan struktur aplikasi Django.
- [model_diagram.md](architecture/model_diagram.md): Representasi visual schema database.
- [CUSTOM_USER_MIGRATION.md](architecture/CUSTOM_USER_MIGRATION.md): Catatan teknis migrasi model custom user.
- [MIGRATION_DEPENDENCY_FIX.md](architecture/MIGRATION_DEPENDENCY_FIX.md): Catatan resolusi konflik dependensi migrasi.
- [SERIALIZER_IMPLEMENTATION.md](architecture/SERIALIZER_IMPLEMENTATION.md): Standar implementasi serializer DRF.

---

### 4. 📊 Laporan & Riwayat Perubahan (`documentation/reports/`)
Ringkasan pengembangan dan catatan rilis teknis:
- [SUMMARY.md](reports/SUMMARY.md): Ikhtisar pencapaian proyek backend.
- [CHANGES_SUMMARY.md](reports/CHANGES_SUMMARY.md): Riwayat perubahan fitur utama.
- [DOCUMENTATION_INTEGRATION_SUMMARY.md](reports/DOCUMENTATION_INTEGRATION_SUMMARY.md): Ringkasan konsolidasi dokumentasi.
- [DOCUMENTATION_SUMMARY.md](reports/DOCUMENTATION_SUMMARY.md): Inventaris dokumen sistem.
- [TRANSLATION_SUMMARY.md](reports/TRANSLATION_SUMMARY.md): Penyesuaian bahasa dan istilah maritim resmi.
