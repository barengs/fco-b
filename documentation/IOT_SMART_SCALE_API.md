# Dokumentasi API Integrasi Timbangan Pintar IoT (Smart Scale) di Pelabuhan

Dokumen ini menjelaskan arsitektur, spesifikasi endpoint API, dan cara kerja integrasi antara **Timbangan Pintar IoT**, **Backend FCO**, dan **Frontend Aplikasi Pelabuhan**.

---

## 1. Alur Kerja (Workflow) di Pelabuhan

```
+-------------------+        1. POST /api/iot/receive-weight/        +-------------------+
|  Timbangan Pintar | ---------------------------------------------> |  Backend FCO      |
|  (IoT / Sensor)   |       (device_id, weight, unit, is_stable)     |  (Django API)     |
+-------------------+                                                +-------------------+
                                                                               |
                                                                               | 2. Broadcast Real-time
                                                                               |    via SSE (Server-Sent Events)
                                                                               v
+-------------------+        4. POST /api/iot/save-catch/            +-------------------+
|  Database, Kuota, | <--------------------------------------------- |  Frontend Petugas |
|  PNBP, Blockchain |    (reading_id, species_id, ship_reg_number)   |  Pelabuhan        |
+-------------------+                                                +-------------------+
```

### Langkah-langkah Proses:
1. **Penimbangan Fisik**: Ikan hasil tangkapan diletakkan di atas timbangan pintar di dermaga/pelabuhan.
2. **Kirim Data IoT**: Sensor timbangan secara otomatis mengirimkan data berat ke endpoint `/api/iot/receive-weight/`.
3. **Penerimaan Real-time di Frontend**: Backend menerima data, menyimpannya ke database dengan status `pending`, dan langsung menyiarkan (broadcast) perubahan berat secara real-time ke frontend via **Server-Sent Events (SSE)**.
4. **Input Data Tambahan oleh Petugas**: Petugas pelabuhan melihat nilai berat yang otomatis terisi di layar. Petugas hanya perlu memilih **Jenis Ikan** dan **Nomor Registrasi Kapal**.
5. **Simpan ke Sistem**: Petugas menekan tombol **Simpan**. Sistem secara otomatis:
   - Membuat/mengaitkan laporan tangkapan (`FishCatch`) dan detailnya (`CatchDetail`).
   - Menghitung tarif PNKP dan PNBP secara otomatis berdasarkan GT kapal dan harga acuan ikan.
   - Memvalidasi dan mengurangi sisa kuota penangkapan kapal.
   - Merekam transaksi tangkapan ke dalam **Blockchain** agar datanya tidak dapat dimanipulasi (*immutable*).
   - Mengubah status pembacaan timbangan menjadi `saved`.

---

## 2. Spesifikasi Endpoint API

### 2.1. Timbangan Mengirim Data Berat (IoT Device Endpoint)
* **URL**: `POST /api/iot/receive-weight/`
* **Autentikasi**: Publik / Opsional `api_key` perangkat
* **Headers**: `Content-Type: application/json`

#### Request Payload (Sangat Minimalis):
```json
{
  "device_id": "SCALE-BENOAS-01",
  "weight": 24.50
}
```

*Catatan: Mikrokontroler (ESP32/Arduino/Raspberry Pi) hanya perlu mengirim 2 atribut: `device_id` (identitas timbangan) dan `weight` (berat ikan).*

#### Response Sukses (`201 Created`):
```json
{
  "status": "success",
  "message": "Data berat berhasil diterima dan disiarkan ke frontend",
  "reading_id": "3f4214e2-6d2c-47ea-8d5c-94d30c5e7b21",
  "device_id": "SCALE-BENOAS-01",
  "weight": 24.5,
  "unit": "kg",
  "is_stable": true,
  "created_at": "2026-10-14T04:30:00.000000+07:00"
}
```

---

### 2.2. Real-time Stream ke Frontend (Server-Sent Events / SSE)
* **URL**: `GET /api/iot/stream/?device_id=SCALE-BENOAS-01`
* **Format**: `text/event-stream`
* **Deskripsi**: Frontend mendengarkan (*listen*) endpoint ini menggunakan standar HTML5 `EventSource`. Setiap kali timbangan mengirim data baru, frontend langsung menerima data tanpa perlu polling berulang.

#### Contoh Implementasi Frontend (JavaScript / React):
```javascript
// Membuka koneksi real-time ke timbangan dermaga
const scaleId = "SCALE-BENOAS-01";
const eventSource = new EventSource(`/api/iot/stream/?device_id=${scaleId}`);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.event === "weight_update") {
    console.log("Berat baru dari timbangan:", data.weight, data.unit);
    
    // Otomatis isi kolom berat di form input:
    document.getElementById("input-weight").value = data.weight;
    document.getElementById("reading-id").value = data.reading_id;
    document.getElementById("scale-status").innerText = data.is_stable ? "Stabil" : "Menimbang...";
  }
};

eventSource.onerror = (err) => {
  console.error("Koneksi timbangan terputus, mencoba menghubungkan kembali...", err);
};
```

---

### 2.3. Mengambil Data Timbangan Terakhir (REST Polling / Initial Load)
* **URL**: `GET /api/iot/latest/?device_id=SCALE-BENOAS-01`
* **Response Sukses (`200 OK`):**
```json
{
  "id": "3f4214e2-6d2c-47ea-8d5c-94d30c5e7b21",
  "device_id": "SCALE-BENOAS-01",
  "scale_name": "Timbangan SCALE-BENOAS-01",
  "port_name": "Pelabuhan Benoa",
  "weight": "24.50",
  "unit": "kg",
  "tare": "0.00",
  "is_stable": true,
  "status": "pending",
  "session_id": "BATCH-20261014-01",
  "fish_catch": null,
  "catch_detail": null,
  "operator_notes": null,
  "created_at": "2026-10-14T04:30:00.000000+07:00"
}
```

---

### 2.4. Simpan Data Tangkapan Pelabuhan (Frontend Action)
* **URL**: `POST /api/iot/save-catch/`
* **Autentikasi**: `Authorization: Token <token_user>` (Petugas Pelabuhan)
* **Headers**: `Content-Type: application/json`

#### Request Payload:
```json
{
  "reading_id": "3f4214e2-6d2c-47ea-8d5c-94d30c5e7b21",
  "ship_registration_number": "KM-MINA-77",
  "fish_species_id": 1,
  "wpp_id": 2,
  "catch_type": "pelagic",
  "catch_date": "2026-10-14",
  "operator_notes": "Tangkapan tuna segar kualitas ekspor"
}
```

#### Response Sukses (`201 Created`):
```json
{
  "status": "success",
  "message": "Laporan tangkapan dari timbangan IoT berhasil disimpan ke database!",
  "catch_id": 42,
  "catch_detail_id": 85,
  "ship_registration": "KM-MINA-77",
  "ship_name": "KM Mina Makmur 77",
  "fish_species": "Tuna Sirip Kuning",
  "weight": 24.5,
  "unit": "kg",
  "pnkp": 1225000.0,
  "pnbp": 61250.0,
  "remaining_quota": 4875.5,
  "reading_id": "3f4214e2-6d2c-47ea-8d5c-94d30c5e7b21",
  "blockchain_status": "Tercatat otomatis di Blockchain"
}
```

---

## 3. Manajemen Perangkat Timbangan Pintar (Admin)

Admin dapat mengelola daftar timbangan yang terdaftar di pelabuhan:
* `GET /api/iot/devices/` - Daftar semua timbangan
* `POST /api/iot/devices/` - Daftarkan timbangan baru
* `GET /api/iot/devices/{id}/` - Detail timbangan
* `PUT /api/iot/devices/{id}/` - Ubah informasi timbangan
* `DELETE /api/iot/devices/{id}/` - Hapus timbangan

---

## 4. Pengujian Simulasi IoT

Anda dapat menguji alur pengiriman data timbangan pintar dengan menjalankan skrip simulasi yang sudah disediakan:

```bash
python3 test_iot_scale.py
```
Skrip ini akan menyimulasikan pembacaan sensor timbangan dan mencetak respon backend secara langsung.
