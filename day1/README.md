# Soal 2: CanSat Ground Control Station (GCS) Telemetry Dashboard (Day 1)

## 1. Deskripsi & Latar Belakang

Pada kompetisi CanSat / Roket, stasiun bumi (**Ground Control Station / GCS**) bertugas untuk menerima aliran data telemetri nirkabel dari wahana secara real-time, mem-parsing setiap parameter penerbangan, dan menampilkannya ke antarmuka grafis (GUI) yang informatif bagi *flight operator*.

Untuk menguji kehandalan GCS sebelum terbang langsung di lapangan, tim pengembang menggunakan program simulator (`cansat_simulator.py`) yang mengalirkan data telemetri sintesis (simulasi penerbangan dari fase peluncuran, meluncur naik, apogee, parasut turun, hingga mendarat).

**Tugasmu:**
Bangunlah aplikasi **Ground Control Station (GCS)** yang dapat terhubung ke simulator, membaca aliran data telemetri secara real-time, dan menyajikannya dalam antarmuka visual (dashboard) yang menarik, responsif, dan mudah dibaca!

---

## 2. Spesifikasi Simulator Telemetri

Simulator (`cansat_simulator.py`) mengalirkan data dengan frekuensi **1 Hz (1 kali setiap detik)** melalui **TCP Socket** (default `127.0.0.1:9999`) atau **Serial Port**.

### A. Cara Menjalankan Simulator
```bash
# Menjalankan simulator di terminal:
python3 cansat_simulator.py
```
*Output simulator:*
```text
=================================================================
📡 CanSat Telemetry Simulator (TCP Mode)
   Listening on : 0.0.0.0:9999
   GCS Address  : 127.0.0.1:9999
   Status       : Waiting for GCS to connect...
=================================================================
```

### B. Format Paket Data Telemetri (CSV Stream)
Saat GCS terhubung, simulator pertama kali mengirimkan satu baris Header:
```text
TEAM_ID,MISSION_TIME,PACKET_COUNT,ALTITUDE,PRESSURE,TEMPERATURE,VOLTAGE,ROLL,PITCH,YAW,GPS_LAT,GPS_LON,GPS_ALT,STATE\r\n
```
Kemudian setiap 1 detik, simulator mengirimkan 1 baris data telemetri:
```text
1064,00:01:23,83,695.4,932.1,28.4,4.15,2.1,-1.5,142.0,-7.275764,112.794317,698.0,APOGEE\r\n
```

### C. Penjelasan Field Telemetri:

| No | Field | Tipe Data | Satuan | Keterangan |
|---|---|---|---|---|
| 1 | `TEAM_ID` | String | - | ID Tim (Contoh: `1064`) |
| 2 | `MISSION_TIME` | String | HH:MM:SS | Waktu misi sejak menyala (Contoh: `00:01:23`) |
| 3 | `PACKET_COUNT` | Integer | - | Nomor urut paket (dimulai dari `1`, increment terus) |
| 4 | `ALTITUDE` | Float | Meter (m) | Ketinggian barometrik wahana dari darat (0 – 700 m) |
| 5 | `PRESSURE` | Float | hPa | Tekanan udara atmosfer (~1013.2 hPa di pad, turun saat naik) |
| 6 | `TEMPERATURE` | Float | °C | Suhu lingkungan (~28.5 °C di darat, mendingin di atas) |
| 7 | `VOLTAGE` | Float | Volt (V) | Tegangan baterai wahana (4.20 V – 3.80 V) |
| 8 | `ROLL` | Float | Derajat (°) | Sudut orientasi Roll (-180° s.d. +180°) |
| 9 | `PITCH` | Float | Derajat (°) | Sudut orientasi Pitch (-90° s.d. +90°) |
| 10 | `YAW` | Float | Derajat (°) | Sudut orientasi Yaw / Heading (0° s.d. 360°) |
| 11 | `GPS_LAT` | Float | Derajat | Latitude posisi GPS (Contoh: `-7.275764`) |
| 12 | `GPS_LON` | Float | Derajat | Longitude posisi GPS (Contoh: `112.794317`) |
| 13 | `GPS_ALT` | Float | Meter (m) | Ketinggian dari sensor GPS |
| 14 | `STATE` | String | - | Fase penerbangan: `LAUNCH_PAD`, `ASCENT`, `APOGEE`, `DESCENT`, `LANDED` |

---

## 3. Ketentuan & Kebutuhan Aplikasi GCS

Kamu **bebas menggunakan bahasa pemrograman dan framework GUI/Web apa pun**, misalnya:
* **Python Desktop:** PyQt6 / PySide6, CustomTkinter, Tkinter, Kivy
* **Python Web/Dashboard:** Streamlit, Dash, Reflex
* **Web App:** React / Vue / Svelte / Vanilla HTML+CSS+JS (dengan backend Node.js / WebSocket)
* **Desktop Framework Lain:** Flutter Desktop, C# (.NET WPF / WinForms), Electron

### Fitur Wajib (Core Requirements):
1. **Connection Control:**
   * Tombol `Connect` dan `Disconnect` ke Simulator (default IP `127.0.0.1` port `9999`).
   * Indikator status koneksi (misal: badge `Connected` / `Disconnected`).
2. **Numerical Telemetry Display:**
   * Menampilkan parameter utama secara rapi: Mission Time, Packet Count, Altitude, Pressure, Temperature, Battery Voltage.
3. **Real-Time Live Chart:**
   * Menampilkan grafik pergerakan real-time untuk parameter **Altitude vs Time** (nilai grafik bertambah setiap detik saat data masuk).
4. **Flight State Indicator:**
   * Indikator visual fase penerbangan saat ini (`LAUNCH_PAD` $\to$ `ASCENT` $\to$ `APOGEE` $\to$ `DESCENT` $\to$ `LANDED`).
5. **Orientation / Location Display:**
   * Menampilkan orientasi (Roll, Pitch, Yaw) dan/atau koordinat GPS (Latitude, Longitude).

### Fitur Tambahan / Nilai Plus (Bonus Points):
* Grafik sekunder (e.g. Temperature / Pressure / Battery over time).
* Indikator orientasi 3D visual / Artificial Horizon (attitude indicator).
* Visualisasi peta posisi GPS (OpenStreetMap / Leaflet / static map).
* Tombol **CSV Export / Logging** (menyimpan seluruh paket yang diterima ke file `.csv` lokal).
* Desain antarmuka UI/UX yang modern, rapi, dan estetis (Dark mode / tema kedirgantaraan).

---

## 4. Contoh Snippet Pembacaan Data di GCS (Referensi Cepat)

### Menggunakan Python (Socket Client):
```python
import socket

# Buat socket TCP dan hubungkan ke simulator
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 9999))
reader = client.makefile("r")

# Lewati baris header
header = reader.readline()

while True:
    line = reader.readline()
    if not line:
        break
    parts = line.strip().split(",")
    if len(parts) >= 14:
        team_id = parts[0]
        mission_time = parts[1]
        packet_count = int(parts[2])
        altitude = float(parts[3])
        pressure = float(parts[4])
        temperature = float(parts[5])
        voltage = float(parts[6])
        roll = float(parts[7])
        pitch = float(parts[8])
        yaw = float(parts[9])
        gps_lat = float(parts[10])
        gps_lon = float(parts[11])
        gps_alt = float(parts[12])
        state = parts[13]

        # Update UI / Chart Anda di sini:
        print(f"[{mission_time}] Alt: {altitude} m | State: {state}")
```

---

## 5. Panduan Integrasi ke Berbagai Framework

> Pola umum: **reader socket berjalan di thread/async terpisah**, lalu data dikirim ke UI lewat mekanisme aman-thread (queue, signal, dispatcher, `after`). Jangan membaca socket langsung di thread UI, agar GUI tidak freeze.

### 5.1 Pola Umum Anti-Freeze (Rujukan Cepat)

```python
import socket, threading, queue

def socket_reader(q, host="127.0.0.1", port=9999):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    f = s.makefile("r")
    f.readline()  # header
    while True:
        line = f.readline()
        if not line:
            break
        parts = line.strip().split(",")
        if len(parts) >= 14:
            q.put(parts)

q = queue.Queue()
threading.Thread(target=socket_reader, args=(q,), daemon=True).start()
# Di thread UI: ambil dari q secara berkala (mis. after()/schedule_interval) lalu update widget.
```

### 5.2 Contoh Minimal Runnable per Framework

#### Python — Tkinter
```python
import socket, threading, tkinter as tk

HOST, PORT = "127.0.0.1", 9999

def reader(update):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    f = s.makefile("r")
    f.readline()  # buang header
    while True:
        line = f.readline()
        if not line:
            break
        parts = line.strip().split(",")
        if len(parts) >= 14:
            update(parts[3], parts[13])  # altitude, state

root = tk.Tk()
root.title("CanSat GCS (Tkinter)")
label = tk.Label(root, font=("Consolas", 20))
label.pack(padx=20, pady=20)

def update(alt, state):
    root.after(0, lambda: label.config(text=f"ALT {alt} m | STATE {state}"))

threading.Thread(target=reader, args=(update,), daemon=True).start()
root.mainloop()
```

#### Python — PyQt6 / PySide6
```python
import socket
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QLabel

class Reader(QThread):
    got = pyqtSignal(str, str)
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 9999))
        f = s.makefile("r"); f.readline()
        while True:
            line = f.readline()
            if not line: break
            p = line.strip().split(",")
            if len(p) >= 14:
                self.got.emit(p[3], p[13])   # altitude, state

app = QApplication([])
label = QLabel("waiting...", alignment=0)
label.setStyleSheet("font-size:24px;")
r = Reader()
r.got.connect(lambda alt, st: label.setText(f"ALT {alt} m | STATE {st}"))
r.start()
label.show()
app.exec()
```

#### Python — CustomTkinter
```python
import socket, threading
import customtkinter as ctk

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("CanSat GCS (CustomTkinter)")
lbl = ctk.CTkLabel(app, text="waiting...", font=("Consolas", 22))
lbl.pack(padx=24, pady=24)

def reader():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 9999))
    f = s.makefile("r"); f.readline()
    while True:
        line = f.readline()
        if not line: break
        p = line.strip().split(",")
        if len(p) >= 14:
            app.after(0, lambda a=p[3], st=p[13]: lbl.configure(text=f"ALT {a} m | STATE {st}"))

threading.Thread(target=reader, daemon=True).start()
app.mainloop()
```

#### Python — Streamlit
```python
import socket, streamlit as st
from streamlit_autorefresh import st_autorefresh

st.title("CanSat GCS (Streamlit)")
st_autorefresh(interval=1000, key="tick")

@st.cache_resource
def get_reader():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 9999))
    f = s.makefile("r"); f.readline()
    return f

f = get_reader()
line = f.readline()
if line:
    p = line.strip().split(",")
    st.metric("Altitude (m)", p[3])
    st.metric("State", p[13])
```
> Install: `pip install streamlit streamlit-autorefresh`

#### Python — Kivy
```python
import socket
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label

class GCS(App):
    def build(self):
        self.label = Label(text="waiting...", font_size=30)
        self.buf = ""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 9999))
        self.f = s.makefile("r"); self.f.readline()
        Clock.schedule_interval(self.tick, 0.5)
        return self.label

    def tick(self, dt):
        line = self.f.readline()
        if line:
            p = line.strip().split(",")
            if len(p) >= 14:
                self.label.text = f"ALT {p[3]} m | STATE {p[13]}"

GCS().run()
```

#### Electron (Node.js)
```javascript
// main.js — jalankan dengan: npx electron .
const { app, BrowserWindow, ipcMain } = require("electron");
const net = require("net");

function createWindow() {
  const win = new BrowserWindow({ width: 800, height: 400 });
  win.loadFile("index.html");

  const sock = net.connect(9999, "127.0.0.1", () => {});
  let buf = "";
  sock.on("data", (chunk) => {
    buf += chunk.toString("utf-8");
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      const p = line.split(",");
      if (p.length >= 14 && p[0] !== "TEAM_ID") {
        win.webContents.send("telemetry", { altitude: p[3], state: p[13] });
      }
    }
  });
}
app.whenReady().then(createWindow);
```
```html
<!-- index.html -->
<!DOCTYPE html><html><body style="font-family:Consolas;font-size:28px">
<div id="out">waiting...</div>
<script>
  const { ipcRenderer } = require("electron");
  ipcRenderer.on("telemetry", (_e, d) => {
    document.getElementById("out").textContent = `ALT ${d.altitude} m | STATE ${d.state}`;
  });
</script>
</body></html>
```

#### Web (Vanilla + Node WebSocket bridge)
```javascript
// server.js — npm install ws ; node server.js
const net = require("net");
const { WebSocketServer } = require("ws");
const wss = new WebSocketServer({ port: 8080 });

net.connect(9999, "127.0.0.1", () => {}).on("data", (chunk) => {
  chunk.toString("utf-8").split("\n").forEach((line) => {
    const p = line.trim().split(",");
    if (p.length >= 14 && p[0] !== "TEAM_ID") {
      wss.clients.forEach((c) => c.send(JSON.stringify({ altitude: p[3], state: p[13] })));
    }
  });
});
```
```html
<!-- index.html -->
<!DOCTYPE html><html><body style="font-family:Consolas;font-size:28px">
<div id="out">waiting...</div>
<script>
  const ws = new WebSocket("ws://127.0.0.1:8080");
  ws.onmessage = (e) => {
    const d = JSON.parse(e.data);
    document.getElementById("out").textContent = `ALT ${d.altitude} m | STATE ${d.state}`;
  };
</script>
</body></html>
```

#### Flutter Desktop (Dart)
```dart
import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';

void main() => runApp(const MaterialApp(home: GcsPage()));

class GcsPage extends StatefulWidget {
  const GcsPage({super.key});
  @override
  State<GcsPage> createState() => _GcsPageState();
}

class _GcsPageState extends State<GcsPage> {
  String text = "waiting...";

  @override
  void initState() {
    super.initState();
    _connect();
  }

  Future<void> _connect() async {
    final socket = await Socket.connect("127.0.0.1", 9999);
    var first = true;
    socket
        .transform(utf8.decoder)
        .transform(const LineSplitter())
        .listen((line) {
      if (first) { first = false; return; } // buang header
      final p = line.trim().split(",");
      if (p.length >= 14) {
        setState(() => text = "ALT ${p[3]} m | STATE ${p[13]}");
      }
    });
  }

  @override
  Widget build(BuildContext context) =>
      Scaffold(body: Center(child: Text(text, style: const TextStyle(fontSize: 28))));
}
```

#### C# (WPF / WinForms)
```csharp
using System;
using System.IO;
using System.Net.Sockets;
using System.Threading.Tasks;
using System.Windows;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        Task.Run(ReadLoop);
    }

    private async Task ReadLoop()
    {
        var client = new TcpClient();
        await client.ConnectAsync("127.0.0.1", 9999);
        using var reader = new StreamReader(client.GetStream());
        reader.ReadLine(); // buang header
        string? line;
        while ((line = await reader.ReadLineAsync()) != null)
        {
            var p = line.Split(',');
            if (p.Length >= 14)
            {
                var text = $"ALT {p[3]} m | STATE {p[13]}";
                Dispatcher.Invoke(() => OutputText.Text = text); // ganti dengan nama kontrolmu
            }
        }
    }
}
```

### 5.3 Troubleshooting

| Masalah | Penyebab & Solusi |
|---|---|
| `Connection refused` | Simulator belum dijalankan, atau port berbeda. Jalankan simulator lebih dulu. |
| `Address already in use` | Port `9999` sedang dipakai proses lain. Jalankan simulator dengan `--port` lain, lalu sesuaikan GCS. |
| Data terlihat "menempel" | Pastikan memecah per `\n`/`\r\n` (buffer per baris), bukan per potongan TCP. |
| Karakter aneh | Pastikan decode **UTF-8**. |
| Command tidak bereaksi | Simulator bersifat satu arah; catat command hanya di log lokal GCS. |
| GUI freeze | Pindahkan pembacaan socket ke thread/async terpisah. |

---

## 6. Prasyarat

* **Python 3.8 atau lebih baru** (disarankan 3.8 – 3.12) untuk menjalankan simulator.
* Mode **TCP (default)** tidak memerlukan paket tambahan.
* Mode **Serial** (opsional) memerlukan `pyserial`:
  ```bash
  pip install pyserial
  ```
* Paket tambahan hanya jika kamu memakai framework terkait (mis. `pip install customtkinter`, `pip install PyQt6`, `pip install streamlit streamlit-autorefresh`).
