#!/usr/bin/env python3
"""
Script simulasi IoT Smart Scale (Timbangan Pintar Pelabuhan).
Menyimulasikan pengiriman data berat ikan dari mikrokontroler (ESP32/Raspberry Pi)
ke backend FCO, serta pengujian penerimaan realtime dan penyimpanan tangkapan.
"""

import urllib.request
import json
import time
import random
import uuid

BASE_URL = "http://127.0.0.1:8000"

def send_scale_weight(device_id="SCALE-BENOAS-01", weight=18.75):
    """Kirim data berat ikan dari timbangan pintar ke backend (hanya ID dan berat)"""
    url = f"{BASE_URL}/api/iot/receive-weight/"
    payload = {
        "device_id": device_id,
        "weight": weight
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print("==> IoT Mengirim Berat:")
            print(f"    Perangkat : {device_id}")
            print(f"    Berat     : {weight} kg")
            print(f"    Reading ID: {res_data.get('reading_id')}")
            print(f"    Status    : {res_data.get('status')}")
            return res_data
    except Exception as e:
        print(f"Gagal mengirim data timbangan: {e}")
        return None

def get_latest_reading(device_id="SCALE-BENOAS-01"):
    """Frontend mengambil data pembacaan terakhir dari timbangan"""
    url = f"{BASE_URL}/api/iot/latest/?device_id={device_id}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print("\n==> Frontend Menerima Berat Terakhir:")
            print(f"    Reading ID: {res_data.get('id')}")
            print(f"    Berat     : {res_data.get('weight')} {res_data.get('unit')}")
            print(f"    Status    : {res_data.get('status')}")
            return res_data
    except Exception as e:
        print(f"Gagal mengambil data pembacaan: {e}")
        return None

if __name__ == '__main__':
    print("Simulasi Timbangan Pintar IoT Pelabuhan FCO")
    print("------------------------------------------")
    sample_weight = round(random.uniform(10.5, 55.0), 2)
    reading = send_scale_weight(weight=sample_weight)
    time.sleep(1)
    get_latest_reading()
