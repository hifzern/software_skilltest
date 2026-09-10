# EEPISAT Software Skill Test — Day 1: CanSat Ground Control Station

Repositori ini berisi paket soal **Skill Test Divisi Software** untuk Open Recruitment Bamantara EEPISAT.

**Day 1** berfokus pada pengembangan **Ground Control Station (GCS) CanSat / Payload**: peserta membangun aplikasi antarmuka (desktop/web) yang terhubung ke simulator telemetri dan memvisualisasikan data penerbangan secara real-time.

---

## 📁 Struktur Repositori

```text
software_skilltest/
├── README.md                  # Dokumen ini
└── day1/
    ├── cansat_simulator.py    # Simulator telemetri CanSat (TCP 127.0.0.1:9999 & Serial)
    └── README.md              # Spesifikasi soal Day 1 (format CSV, kebutuhan GCS, rubrik)
```

---

## 🛰️ Day 1 — CanSat / Payload GCS

**Tugas:** Bangun aplikasi **Ground Control Station (GCS)** yang terhubung ke simulator telemetri, mem-parsing data secara real-time, dan menampilkannya dalam dashboard visual yang informatif.

### Cara Menjalankan Simulator
```bash
# Mode TCP (default) — mendengarkan di 127.0.0.1:9999
python3 day1/cansat_simulator.py

# Ganti port
python3 day1/cansat_simulator.py --port 9999

# Mode Serial (opsional)
python3 day1/cansat_simulator.py --serial /dev/ttyUSB0 115200
python day1/cansat_simulator.py --serial COM3 115200
```

Saat aplikasi GCS terhubung, simulator mengirim **1 baris header** lalu **1 baris data per detik (1 Hz)** dalam format CSV.

### Format CSV (14 kolom)
```text
TEAM_ID,MISSION_TIME,PACKET_COUNT,ALTITUDE,PRESSURE,TEMPERATURE,VOLTAGE,ROLL,PITCH,YAW,GPS_LAT,GPS_LON,GPS_ALT,STATE
```
Contoh baris data:
```text
1064,00:01:23,83,695.4,932.1,28.4,4.15,2.1,-1.5,142.0,-7.275764,112.794317,698.0,APOGEE
```

> **Catatan:** Simulator bersifat **satu arah (streaming saja)** — ia tidak membalas perintah dari GCS.

📄 **Detail lengkap** (tabel kolom, kebutuhan fitur GCS, rubrik penilaian, dan format pengumpulan) ada di [`day1/README.md`](day1/README.md).
