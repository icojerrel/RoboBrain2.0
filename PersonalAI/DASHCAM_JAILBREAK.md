# 🔓 Dashcam Jailbreak Guide voor PersonalAI

**Disclaimer:** Jailbreaken void je warranty en kan je dashcam bricken. Doe dit alleen als je weet wat je doet. Voor eigen risico.

---

## 🎯 Waarom Jailbreaken?

**Doel:** RTSP video stream enablen zodat PersonalAI de video kan analyseren.

**Wat je krijgt:**
- ✅ Real-time video stream naar PersonalAI
- ✅ Telnet/SSH access voor debugging
- ✅ Custom settings (bitrate, FPS, etc.)
- ✅ Integration met PersonalAI AI features

**Wat je NIET krijgt:**
- ❌ AI runnen OP de dashcam (hardware te zwak)
- ❌ Meer storage (alleen SD card)
- ❌ Betere camera (hardware limitatie)

**Betere aanpak:** Dashcam blijft normale opname doen, PersonalAI analyseert de stream parallel.

---

## 🎯 Jailbreakbare Dashcams

### ✅ **Tier 1: Makkelijk** (geen soldeerwerk)

| Model | Methode | Moeilijkheid | Community |
|-------|---------|--------------|-----------|
| **Yi Dashcam** | SD card autoboot | ⭐ Makkelijk | ⭐⭐⭐⭐⭐ Grote community |
| **Yi 2.7K** | SD card autoboot | ⭐ Makkelijk | ⭐⭐⭐⭐⭐ |
| **GitUp Git2** | Firmware flash | ⭐⭐ Gemiddeld | ⭐⭐⭐ Klein |

### ⚠️ **Tier 2: Moeilijk** (UART/soldeerwerk)

| Model | Methode | Moeilijkheid | Community |
|-------|---------|--------------|-----------|
| **70mai A500S** | UART access | ⭐⭐⭐ Moeilijk | ⭐⭐ Beperkt |
| **Viofo A129** | UART + firmware | ⭐⭐⭐⭐ Zeer moeilijk | ⭐ Minimaal |

### ❌ **Tier 3: Onmogelijk** (encrypted firmware)

- BlackVue (DR900X, DR750X, etc.)
- Thinkware (Q800, U1000, etc.)
- Garmin Dash Cam (encrypted updates)
- Nextbase (signed firmware)

**Waarom niet:** Encrypted bootloader, signed firmware, anti-tamper.

---

## 📋 Methode 1: Yi Dashcam Jailbreak (MAKKELIJKST)

### Benodigdheden:
- ✅ Yi Dashcam (€30-60)
- ✅ MicroSD card (16GB+, FAT32)
- ✅ Computer met SD card reader
- ✅ 10 minuten tijd

### Stap 1: Download Custom Firmware

```bash
# Clone Yi hack repository
git clone https://github.com/TheCrypt0/yi-hack-v4.git
cd yi-hack-v4

# Or download release:
wget https://github.com/TheCrypt0/yi-hack-v4/releases/latest/download/yi-hack-v4.zip
unzip yi-hack-v4.zip
```

### Stap 2: Prepare SD Card

```bash
# Format SD card als FAT32
# Windows: Right-click → Format → FAT32
# Linux:
sudo mkfs.vfat -F 32 /dev/sdX1

# Mount SD card
mount /dev/sdX1 /mnt/sd

# Kopieer firmware files
cp -r yi-hack-v4/* /mnt/sd/

# Add PersonalAI bridge script
cp PersonalAI/hardware_configs/personalai_bridge.sh /mnt/sd/

# Unmount
umount /mnt/sd
```

### Stap 3: Install op Dashcam

```bash
1. Dashcam uitschakelen
2. SD card plaatsen
3. Dashcam aanzetten
4. Wacht 2-3 minuten (LED knippert tijdens install)
5. Dashcam reboot automatisch
6. ✅ Jailbreak complete!
```

### Stap 4: Configureer WiFi

```bash
# Verbind met Yi WiFi hotspot
SSID: Yi_Camera_XXXXXX
Pass: 1234567890

# Browse naar:
http://192.168.1.254

# In web interface:
- Enable RTSP server
- Set WiFi credentials (jouw auto hotspot)
- Enable Telnet (optioneel, voor debugging)
```

### Stap 5: Test RTSP Stream

```bash
# Test met VLC
vlc rtsp://192.168.1.254:554/stream

# Test met ffmpeg
ffplay rtsp://192.168.1.254:554/stream

# Test met OpenCV (Python)
import cv2
cap = cv2.VideoCapture("rtsp://192.168.1.254:554/stream")
ret, frame = cap.read()
cv2.imshow("Yi Stream", frame)
```

### Stap 6: Integreer met PersonalAI

```python
# PersonalAI setup
from modules.dashcam_ai import get_dashcam

# Connect naar Yi dashcam RTSP
dashcam = get_dashcam(
    front_camera="rtsp://192.168.1.254:554/stream"
)

# Start monitoring
dashcam.start_monitoring()

# ✅ PersonalAI analyseert nu Yi dashcam stream!
```

---

## 📋 Methode 2: 70mai Dashcam UART Access (MOEILIJK)

**⚠️ Waarschuwing:** Vereist soldeerwerk en kan dashcam bricken!

### Benodigdheden:
- 70mai dashcam (A500S, A800S, etc.)
- USB UART adapter (CP2102 of FTDI)
- Soldeerbout en draadjes
- Schroevendraaier set
- Multimeter (optioneel)

### Stap 1: Open Dashcam

```
⚠️ VOID WARRANTY!

1. Verwijder rubber cover
2. Schroef 4x kleine schroefjes uit
3. Open voorzichtig (clips!)
4. Zoek PCB debug pads
```

### Stap 2: Identificeer UART Pads

```
Zoek op PCB:
- TX (Transmit) - meestal gelabeld
- RX (Receive)
- GND (Ground)
- VCC (3.3V - NIET AANSLUITEN!)

Test met multimeter:
- GND = 0V (altijd)
- TX = 3.3V idle (data pin)
- RX = 3.3V idle (data pin)
```

### Stap 3: Soldeer UART Header

```
UART Adapter Connections:
┌──────────────┐
│ USB UART     │
│   Adapter    │
├──────────────┤
│ TX  → RX     │ (Cross-over!)
│ RX  → TX     │ (Cross-over!)
│ GND → GND    │
└──────────────┘

⚠️ NIET VCC aansluiten - dashcam heeft eigen power!
```

### Stap 4: Connect via Serial

```bash
# Linux
sudo screen /dev/ttyUSB0 115200

# Windows (PuTTY)
Port: COM3
Speed: 115200
Data bits: 8
Parity: None
Stop bits: 1

# macOS
screen /dev/cu.usbserial-XXXXX 115200
```

### Stap 5: Boot Dashcam

```bash
# Power on dashcam, je ziet boot log:

U-Boot 2013.07 (Jul 15 2020 - 14:22:33)
...
Starting kernel ...

Linux version 3.10.14
...

# Login prompt:
70mai login: root
Password: (meestal leeg of "root")

# ✅ Root access!
```

### Stap 6: Enable RTSP

```bash
# Check running processes
ps | grep rtsp

# Start RTSP server (if not running)
/usr/bin/rtspd &

# Check RTSP port
netstat -an | grep 554

# Get dashcam IP
ifconfig wlan0 | grep inet

# Test stream
# rtsp://[DASHCAM_IP]:554/stream
```

### Stap 7: Make Persistent

```bash
# Edit boot script (make persistent)
vi /etc/init.d/rcS

# Add:
/usr/bin/rtspd &

# Save and reboot
reboot
```

---

## 📋 Methode 3: RTSP Discovery (Geen Jailbreak)

Sommige dashcams hebben **verborgen RTSP** die je kunt activeren zonder jailbreak:

### Viofo Dashcams:

```bash
# Connect to dashcam WiFi
# Try RTSP URLs:
rtsp://192.168.1.254:8554/
rtsp://192.168.1.254:554/live
rtsp://192.168.1.254/stream

# Test with VLC
```

### 70mai (zonder UART):

```bash
# Download 70mai app APK
# Decompile APK (apktool)
apktool d 70mai.apk

# Search for RTSP URLs in code:
grep -r "rtsp://" 70mai/

# Example found URLs:
rtsp://192.168.1.1:8554/live
```

### BlackVue Cloud Streaming:

```bash
# BlackVue heeft cloud streaming via hun app
# Niet direct RTSP, maar HTTP video stream

# URL format (varies by model):
http://[DASHCAM_IP]/blackvue_vod.cgi

# PersonalAI kan HTTP stream lezen:
dashcam = get_dashcam(
    front_camera="http://192.168.1.10/blackvue_vod.cgi"
)
```

---

## 🚀 PersonalAI Integration

### Setup: Jailbroken Dashcam + PersonalAI

**Architecture:**
```
┌──────────────────┐
│  Yi Dashcam      │
│  (Jailbroken)    │
│                  │
│  RTSP Stream ────┼──┐
│  Port 554        │  │
└──────────────────┘  │
                      │
                      │ WiFi
                      │
                      ▼
┌──────────────────────────────┐
│  Laptop/RPi in Auto          │
│                              │
│  PersonalAI                  │
│  ├─ dashcam_ai.py            │
│  ├─ license_plate_ai.py      │
│  ├─ RoboBrain 7B             │
│  └─ Telegram Bot             │
│                              │
│  Analyseert RTSP stream      │
│  - Incident detection        │
│  - ANPR                      │
│  - Traffic signs             │
│  - Telegram alerts           │
└──────────────────────────────┘
```

### Option 1: Direct RTSP Connection

```python
# PersonalAI/run_jailbroken_dashcam.py

from modules.dashcam_ai import get_dashcam, RecordingMode

# Connect to jailbroken Yi dashcam
dashcam = get_dashcam(
    front_camera="rtsp://192.168.1.254:554/stream"
)

# Start AI monitoring
# Dashcam doet normale opname naar SD
# PersonalAI analyseert stream real-time
dashcam.start_monitoring()

print("✅ PersonalAI monitoring jailbroken dashcam!")
print("📡 RTSP stream: rtsp://192.168.1.254:554/stream")
print("🤖 AI analysis active")
print("📱 Telegram alerts enabled")
```

### Option 2: Bridge Server (Advanced)

```bash
# Start PersonalAI bridge server
python PersonalAI/interfaces/dashcam_bridge_server.py

# Server luistert op:
# http://0.0.0.0:5000

# Dashcam registreert zichzelf en streamt snapshots
```

**Op jailbroken dashcam:**
```bash
# Plaats in /tmp/sd/personalai_bridge.sh
# Start automatically on boot
```

**Voordelen:**
- ✅ Dashcam pusht snapshots naar PersonalAI
- ✅ Lagere bandwidth (alleen snapshots)
- ✅ Werkt ook zonder continuous connection
- ✅ Multiple dashcams supported

---

## 🔧 Troubleshooting

### RTSP Stream Niet Beschikbaar

```bash
# Check if RTSP server running (via telnet/UART)
ps | grep rtsp
# Should show: rtspd or rtspsvr

# Restart RTSP server
killall rtspd
/usr/bin/rtspd &

# Check port
netstat -an | grep 554
```

### WiFi Connection Issues

```bash
# Check WiFi status
ifconfig wlan0

# Reconnect to WiFi
/usr/local/share/script/wifi.sh

# Check if internet reachable
ping 8.8.8.8
```

### Dashcam Bricked After Jailbreak

```bash
# Yi Dashcam recovery:
1. Download official Yi firmware
2. Rename to: firmware.bin
3. Place on SD card root
4. Power on dashcam
5. Wait 5-10 minutes
6. ✅ Factory firmware restored
```

### UART No Output

```bash
# Check connections:
- TX ↔ RX (crossed!)
- RX ↔ TX (crossed!)
- GND ↔ GND

# Check baud rate (try):
- 115200 (most common)
- 57600
- 38400

# Check voltage (multimeter):
- Should be 3.3V on TX/RX when idle
```

---

## ⚖️ Legal & Veiligheid

### Legal:

✅ **Toegestaan:**
- Modificeren van eigen hardware
- Firmware reverse engineering voor interoperability
- RTSP stream enablen
- Custom software runnen

❌ **Niet toegestaan:**
- Firmware redistribution (copyright)
- Commercial use van modified firmware
- Bypassen DRM voor paid features

### Veiligheid:

⚠️ **Risico's:**
- **Brick risk:** Dashcam kan permanent kapot
- **Warranty void:** Fabrikant garantie vervalt
- **Security:** Open telnet = security risk
- **Stability:** Custom firmware kan crashen

🛡️ **Mitigatie:**
- Backup original firmware
- Test eerst op oude dashcam
- Disable telnet in productie
- Keep original dashcam als backup

---

## 🎯 Aanbeveling

### Voor Meeste Mensen:

**❌ NIET jailbreaken**

**✅ Betere opties:**
1. **Koop WiFi dashcam** met RTSP support (€60-100)
2. **Gebruik Raspberry Pi** met eigen camera (€80)
3. **Gebruik webcam** op dashboard (€50)

### Alleen Jailbreaken Als:

✅ Je al een Yi dashcam hebt (makkelijke jailbreak)
✅ Je technische skills hebt (UART soldering)
✅ Je experimenteert / leert
✅ Je backup dashcam hebt
✅ Je weet wat je doet

---

## 📚 Resources

### Yi Dashcam:
- https://github.com/TheCrypt0/yi-hack-v4
- https://github.com/irungentoo/Xiaomi_Yi_autoboot
- https://dashcamtalk.com/forum/forums/yi-dashcam.51/

### 70mai:
- https://dashcamtalk.com/forum/forums/70mai.235/
- UART pinouts: https://forum.openmediavault.org/

### GitUp:
- https://github.com/Fishwaldo/GIT2-Firmware

### RTSP Testing:
- VLC Media Player: https://www.videolan.org/
- ffmpeg: https://ffmpeg.org/
- RTSP Simple Server: https://github.com/aler9/rtsp-simple-server

---

## ✅ Conclusie

**Jailbreaken voor PersonalAI:**

**Voordelen:**
- ✅ RTSP stream access
- ✅ Custom settings
- ✅ Integration met PersonalAI

**Nadelen:**
- ❌ Void warranty
- ❌ Brick risk
- ❌ Technische skills vereist
- ❌ Time consuming

**Beter alternatief:**
```python
# Gewoon een WiFi dashcam kopen met RTSP
# Of Raspberry Pi met camera gebruiken
# Minder gedoe, zelfde result
```

Maar als je wilt experimenteren: Yi Dashcam jailbreak is relatief safe en goed gedocumenteerd! 🚗🔓
