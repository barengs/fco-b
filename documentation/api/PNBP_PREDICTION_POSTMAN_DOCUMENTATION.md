# 📊 **PNBP Prediction API - Postman Documentation**

## 🎯 **Overview**
API untuk prediksi Penerimaan Negara Bukan Pajak (PNBP) sektor perikanan menggunakan 4 metode analisis canggih.

## 🚀 **Base URL**
```
http://localhost:8000/api/catches/pnbp/
```

## 🔐 **Authentication**
```
Authorization: Bearer <your-jwt-token>
```
*(Opsional jika endpoint tidak memerlukan authentication)*

---

## 🧪 **Step-by-Step Testing Guide in Postman**

### **Persiapan Awal**
1. **Pastikan Server Django Berjalan**
   ```bash
   cd /path/to/your/django/project
   python manage.py runserver 8000
   ```
   Server harus berjalan di `http://localhost:8000`

2. **Buka Postman**
   - Download dan install Postman dari https://www.postman.com/downloads/
   - Buka aplikasi Postman

3. **Import Collection**
   - Klik tombol **Import** di Postman
   - Pilih tab **Raw text**
   - Copy-paste JSON collection dari bagian **Postman Collection Examples** di bawah ini
   - Klik **Import**

4. **Setup Environment Variables (Opsional)**
   - Klik **Environments** di sidebar kiri
   - Klik **+** untuk membuat environment baru
   - Tambahkan variables:
     - `base_url`: `http://localhost:8000`
     - `auth_token`: `your-jwt-token-here` (jika menggunakan authentication)

### **Langkah Testing**

#### **Step 1: Test Endpoint Prediksi PNBP**
1. **Pilih Request "Prediksi PNBP Masa Depan"**
   - Di sidebar kiri, klik folder **PNBP Prediction API**
   - Klik request **Prediksi PNBP Masa Depan**

2. **Konfigurasi Request**
   - Method: `POST`
   - URL: `{{base_url}}/api/catches/pnbp/predict/` (atau `http://localhost:8000/api/catches/pnbp/predict/`)

3. **Set Headers**
   - Klik tab **Headers**
   - Tambahkan:
     - `Content-Type`: `application/json`
     - `Authorization`: `Bearer {{auth_token}}` (jika diperlukan)

4. **Set Request Body**
   - Klik tab **Body**
   - Pilih **raw** dan **JSON**
   - Masukkan JSON:
     ```json
     {
       "use_database_data": true,
       "save_results": true,
       "ships_data": [
         {
           "Kapal": "Kapal-712-75GT-01",
           "Prediksi": 180.0,
           "Kuota_Kg": 175.0
         }
       ]
     }
     ```

5. **Kirim Request**
   - Klik tombol **Send**
   - **Expected Response (200)**:
     ```json
     {
       "status": "success",
       "predictions": {
         "individual_predictions": {
           "regression": 10500000,
           "neural_network": 11200000,
           "nsga3_optimization": 10800000,
           "time_series": 10600000
         },
         "normalized_predictions": {
           "regression": 0.25,
           "neural_network": 0.75,
           "nsga3_optimization": 0.50,
           "time_series": 0.30
         },
         "final_prediction": 0.525,
         "timestamp": "2025-10-10T09:00:00.000000",
         "methods_used": [
           "regression",
           "neural_network",
           "nsga3_optimization",
           "time_series"
         ]
       },
       "message": "PNBP prediction completed successfully"
     }
     ```

6. **Verifikasi Response**
   - Status code harus `200 OK`
   - Cek `status: "success"`
   - Pastikan `predictions` object berisi semua field yang diperlukan
   - Hitung nilai rupiah menggunakan formula di bagian **Cara Menghitung Nilai Rupiah**

#### **Step 2: Test Endpoint Data Historis**
1. **Pilih Request "Data Historis PNBP"**
   - Klik request **Data Historis PNBP**

2. **Konfigurasi Request**
   - Method: `GET`
   - URL: `{{base_url}}/api/catches/pnbp/history/?source=database`

3. **Kirim Request**
   - Klik **Send**

4. **Expected Response (200)**:
   ```json
   {
     "status": "success",
     "source": "database",
     "data_count": 3,
     "historical_data": [
       {
         "timestamp": "2025-10-10 10:25",
         "nama_kapal": "Kapal-712-75GT-01",
         "gt_kapal": 75.0,
         "total_volume": 180.0,
         "total_pnbp": 10440000.0
       }
     ]
   }
   ```

5. **Verifikasi Response**
   - Status code `200 OK`
   - Cek `status: "success"`
   - Pastikan `historical_data` array tidak kosong

#### **Step 3: Test Endpoint Hasil Prediksi Terakhir**
1. **Pilih Request "Hasil Prediksi Terakhir"**
   - Klik request **Hasil Prediksi Terakhir**

2. **Konfigurasi Request**
   - Method: `GET`
   - URL: `{{base_url}}/api/catches/pnbp/latest-predictions/`

3. **Kirim Request**
   - Klik **Send**

4. **Expected Response (200)**:
   ```json
   {
     "status": "success",
     "predictions": {
       "timestamp": "2025-10-10T09:00:00.000000",
       "predictions": {
         "individual_predictions": {
           "regression": 10500000,
           "neural_network": 11200000,
           "nsga3_optimization": 10800000,
           "time_series": 10600000
         },
         "normalized_predictions": {
           "regression": 0.25,
           "neural_network": 0.75,
           "nsga3_optimization": 0.50,
           "time_series": 0.30
         },
         "final_prediction": 0.525
       }
     }
   }
   ```

5. **Verifikasi Response**
   - Status code `200 OK`
   - Cek `status: "success"`
   - Data harus sesuai dengan hasil prediksi sebelumnya

### **Troubleshooting**

#### **Error 500: Internal Server Error**
- Pastikan semua dependencies terinstall: `pip install -r requirements.txt`
- Cek apakah file `pnbp_history.json` ada dan berisi data valid
- Jalankan migrasi database: `python manage.py migrate`
- Cek log server Django untuk error details

#### **Error 404: Not Found**
- Pastikan URL endpoint benar
- Cek apakah server berjalan di port 8000
- Verifikasi path URL sesuai dokumentasi

#### **Error 503: Service Unavailable**
- Dependencies ML belum terinstall (numpy, pandas, scikit-learn, statsmodels, platypus-opt)
- Install dependencies: `pip install numpy pandas scikit-learn statsmodels platypus-opt`
- Restart server Django setelah install dependencies

#### **Response Kosong atau Tidak Sesuai**
- Pastikan database berisi data historis
- Cek format request body JSON
- Verifikasi headers Content-Type

### **Tips Testing**
- Gunakan **Postman Runner** untuk menjalankan semua request secara otomatis
- Simpan response sebagai **Example** untuk referensi
- Gunakan **Tests** tab untuk menambahkan assertion otomatis
- Export collection setelah testing untuk backup

---

## 📋 **1. POST - Prediksi PNBP Masa Depan**

### **Endpoint**
```
POST /api/catches/pnbp/predict/
```

### **Description**
Melakukan prediksi PNBP masa depan menggunakan 4 metode:
- Analisis Regresi (25%)
- Jaringan Saraf (35%)
- Optimasi NSGA-III (25%)
- Peramalan Deret Waktu (15%)

### **Headers**
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer your-token-here"
}
```

### **Request Body**
```json
{
  "use_database_data": true,
  "save_results": true,
  "ships_data": [
    {
      "Kapal": "Kapal-712-75GT-01",
      "Prediksi": 180.0,
      "Kuota_Kg": 175.0
    }
  ]
}
```

### **Parameters**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `use_database_data` | boolean | No | `true` | Gunakan data dari database Django |
| `save_results` | boolean | No | `false` | Simpan hasil ke file JSON |
| `ships_data` | array | No | `null` | Data kapal untuk optimasi NSGA-III |

### **Success Response (200)**
```json
{
  "status": "success",
  "predictions": {
    "individual_predictions": {
      "regression": 10500000,
      "neural_network": 11200000,
      "nsga3_optimization": 10800000,
      "time_series": 10600000
    },
    "normalized_predictions": {
      "regression": 0.25,
      "neural_network": 0.75,
      "nsga3_optimization": 0.50,
      "time_series": 0.30
    },
    "final_prediction": 0.525,
    "timestamp": "2025-10-10T09:00:00.000000",
    "methods_used": [
      "regression",
      "neural_network",
      "nsga3_optimization",
      "time_series"
    ]
  },
  "message": "PNBP prediction completed successfully"
}
```

### **Error Response (500)**
```json
{
  "error": "Prediction failed: <error_message>"
}
```

---

## 📊 **2. GET - Data Historis PNBP**

### **Endpoint**
```
GET /api/catches/pnbp/history/
```

### **Description**
Mengambil data historis PNBP dari database atau file JSON.

### **Query Parameters**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | No | `database` | Sumber data: `database` atau `file` |

### **Example Request**
```
GET /api/catches/pnbp/history/?source=database
```

### **Success Response (200)**
```json
{
  "status": "success",
  "source": "database",
  "data_count": 3,
  "historical_data": [
    {
      "timestamp": "2025-10-10 10:25",
      "nama_kapal": "Kapal-712-75GT-01",
      "gt_kapal": 75.0,
      "total_volume": 180.0,
      "total_pnbp": 10440000.0
    }
  ]
}
```

---

## 📈 **3. GET - Hasil Prediksi Terakhir**

### **Endpoint**
```
GET /api/catches/pnbp/latest-predictions/
```

### **Description**
Mengambil hasil prediksi PNBP yang tersimpan terakhir dari file JSON.

### **Success Response (200)**
```json
{
  "status": "success",
  "predictions": {
    "timestamp": "2025-10-10T09:00:00.000000",
    "predictions": {
      "individual_predictions": {
        "regression": 10500000,
        "neural_network": 11200000,
        "nsga3_optimization": 10800000,
        "time_series": 10600000
      },
      "normalized_predictions": {
        "regression": 0.25,
        "neural_network": 0.75,
        "nsga3_optimization": 0.50,
        "time_series": 0.30
      },
      "final_prediction": 0.525
    }
  }
}
```

### **Not Found Response (404)**
```json
{
  "status": "not_found",
  "message": "No saved predictions found"
}
```

---

## 🧮 **Cara Menghitung Nilai Rupiah dari Final Prediction**

Karena `final_prediction` adalah nilai ternormalisasi (0-1), gunakan formula berikut:

```javascript
// JavaScript example
const predictions = response.data.predictions;
const individualValues = Object.values(predictions.individual_predictions);
const minVal = Math.min(...individualValues);
const maxVal = Math.max(...individualValues);
const actualFinalRupiah = predictions.final_prediction * (maxVal - minVal) + minVal;

console.log(`Prediksi PNBP: Rp ${actualFinalRupiah.toLocaleString()}`);
```

```python
# Python example
predictions = response['predictions']
individual_values = list(predictions['individual_predictions'].values())
min_val = min(individual_values)
max_val = max(individual_values)
actual_final_rupiah = predictions['final_prediction'] * (max_val - min_val) + min_val

print(f"Prediksi PNBP: Rp {actual_final_rupiah:,.0f}")
```

---

## 📝 **Postman Collection Examples**

### **Collection JSON untuk Import ke Postman:**

```json
{
  "info": {
    "name": "PNBP Prediction API",
    "description": "API untuk prediksi PNBP sektor perikanan"
  },
  "item": [
    {
      "name": "Prediksi PNBP Masa Depan",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"use_database_data\": true, \"save_results\": true}"
        },
        "url": {
          "raw": "http://localhost:8000/api/catches/pnbp/predict/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "catches", "pnbp", "predict", ""]
        }
      }
    },
    {
      "name": "Data Historis PNBP",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:8000/api/catches/pnbp/history/?source=database",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "catches", "pnbp", "history", ""],
          "query": [
            {
              "key": "source",
              "value": "database"
            }
          ]
        }
      }
    },
    {
      "name": "Hasil Prediksi Terakhir",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:8000/api/catches/pnbp/latest-predictions/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "catches", "pnbp", "latest-predictions", ""]
        }
      }
    }
  ]
}
```

---

## ⚡ **Quick Test Commands**

### **cURL Examples:**

```bash
# Prediksi PNBP
curl -X POST "http://localhost:8000/api/catches/pnbp/predict/" \
     -H "Content-Type: application/json" \
     -d '{"use_database_data": true, "save_results": true}'

# Data Historis
curl -X GET "http://localhost:8000/api/catches/pnbp/history/?source=database"

# Hasil Terakhir
curl -X GET "http://localhost:8000/api/catches/pnbp/latest-predictions/"
```

---

## 📊 **Response Data Structure**

### **Individual Predictions**
| Method | Weight | Description |
|--------|--------|-------------|
| `regression` | 25% | Analisis regresi linear |
| `neural_network` | 35% | Jaringan saraf tiruan |
| `nsga3_optimization` | 25% | Optimasi multi-objektif |
| `time_series` | 15% | ARIMA forecasting |

### **Normalized Predictions**
Nilai 0-1 dari masing-masing metode setelah MinMaxScaler.

### **Final Prediction**
Rata-rata tertimbang dari normalized predictions.

---

## 🚨 **Error Codes**

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |
| 503 | Service Unavailable (module not loaded) |

---

## 📋 **Testing Checklist**

- [ ] Server Django running (`python manage.py runserver`)
- [ ] Database migrations applied
- [ ] Historical data tersedia di `pnbp_history.json` atau database
- [ ] Authentication token valid (jika diperlukan)
- [ ] Postman collection imported
- [ ] Test semua 3 endpoint
- [ ] Verify response format sesuai dokumentasi

---

## 🎯 **Next Steps**

1. **Frontend Integration**: Gunakan data API untuk membuat dashboard
2. **Real-time Updates**: Implementasi WebSocket untuk live predictions
3. **Advanced Analytics**: Tambahkan confidence intervals dan error bounds
4. **Model Training**: Periodic retraining dengan data terbaru

---

*📅 Last Updated: 2025-10-10*
*🔧 Version: 1.0.0*
*👨‍💻 Developer: AI Assistant*