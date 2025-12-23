# 📹 PersonalAI Camera Monitoring

**Real-time AI Vision Monitoring voor je EZVIZ Husky Air (en andere cameras)**

Live camera monitoring met RoboBrain 2.0 AI voor:
- 🎥 Real-time scene understanding
- 👤 Person detection & counting
- 🚨 Event detection & alerts
- 🔍 Object finding & tracking
- 📊 Activity monitoring
- 💾 Event logging

---

## 🚀 Quick Start: EZVIZ Husky Air

### Stap 1: Vind je Camera IP

**Via EZVIZ App:**
1. Open EZVIZ app op je telefoon
2. Ga naar camera instellingen
3. Kijk bij "Device Information" → "IP Address"

**Via Router:**
1. Log in op je router (meestal 192.168.1.1)
2. Kijk bij "Connected Devices"
3. Zoek "EZVIZ" of "Husky Air"

### Stap 2: Test RTSP Stream

```bash
# Test of RTSP werkt (optioneel)
ffplay "rtsp://admin:JOUW_WACHTWOORD@192.168.1.XXX:554/h264/ch01/main/av_stream"
```

### Stap 3: Setup in PersonalAI

**Python:**
```python
from modules.ezviz_integration import setup_husky_air

# Interactive setup (vraagt om IP en wachtwoord)
camera = setup_husky_air()

# OF met parameters
camera = setup_husky_air(
    name="Woonkamer",
    ip="192.168.1.100",
    password="jouw_wachtwoord"
)

# Start monitoring
camera.start_stream("sub")  # Lage kwaliteit voor monitoring
```

**Telegram Bot:**
```
/camera_setup
# Volg de instructies

/camera_list
# Zie alle cameras

/camera_snapshot Woonkamer
# Neem snapshot
```

---

## 📱 Telegram Commands

### Setup & Beheer
```
/camera_setup          - Setup nieuwe camera (interactive)
/camera_list           - Toon alle camera's
/camera_start <name>   - Start camera stream
/camera_stop <name>    - Stop camera stream
/camera_remove <name>  - Verwijder camera
```

### Monitoring
```
/camera_snapshot <name>     - Neem snapshot
/camera_analyze <name>      - AI scene analyse
/camera_find <name> <obj>   - Vind object
/camera_count <name>        - Tel mensen
```

### Live Monitoring
```
/monitor_start         - Start AI monitoring (alle cameras)
/monitor_stop          - Stop monitoring
/monitor_status        - Monitoring status
/monitor_events        - Recente events
```

### Voorbeelden
```
/camera_snapshot Woonkamer
/camera_analyze Voordeur
/camera_find Woonkamer rode auto
/camera_count Voordeur
```

---

## 🎯 Features

### 1. **Live Scene Analysis**
Real-time begrip van wat de camera ziet:
```python
from modules.vision_monitor import get_vision_monitor

monitor = get_vision_monitor()

# Analyseer huidige view
result = monitor.analyze_snapshot(
    "Woonkamer",
    "Wat gebeurt er in deze kamer?"
)

print(result['answer'])
# "Er zitten twee mensen op de bank.
#  De TV staat aan. Alles lijkt normaal."
```

### 2. **Object Detection & Finding**
Vind specifieke objecten:
```python
# Zoek object
result = monitor.find_object(
    "Woonkamer",
    "de rode mok op de tafel"
)

# Krijg locatie (bounding box)
print(result['answer'])  # "[245, 156, 312, 234]"
```

### 3. **Person Detection & Counting**
```python
# Tel mensen
result = monitor.count_people("Voordeur")
print(result['answer'])  # "2 mensen zichtbaar"
```

### 4. **Event Detection**
Automatische event detection:
- 🚶 Motion detection
- 👤 Person detected
- ⚠️ Unusual activity
- 🚨 Custom events

```python
# Event callback
def on_event(event):
    print(f"Alert: {event.description}")
    # Stuur notificatie, save snapshot, etc.

monitor.add_event_callback(on_event)
monitor.start_monitoring()
```

### 5. **Change Detection**
Vergelijk met referentie:
```python
result = monitor.detect_changes(
    "Woonkamer",
    reference_image="reference.jpg"
)

print(result['answer'])
# "De deur staat nu open.
#  Er is een nieuwe plant bij het raam."
```

---

## 🔧 Configuration

### Camera Settings

**config.py toevoegen:**
```python
# Camera monitoring
ENABLE_CAMERA_MONITORING = True
CAMERA_ANALYSIS_INTERVAL = 5.0  # Seconden tussen AI analyses
CAMERA_MOTION_THRESHOLD = 30    # Motion sensitivity
MAX_CAMERA_EVENTS = 100         # Event history size
```

### EZVIZ Husky Air Specs

**Streams:**
- **Main Stream**: 1920x1080, 15-20 FPS (hoge kwaliteit)
- **Sub Stream**: 640x480, 10 FPS (monitoring, lagere bandwidth)

**Aanbevolen:**
- Gebruik **sub stream** voor continuous monitoring
- Gebruik **main stream** voor snapshots en belangrijke analyses
- FPS: 10-15 is voldoende voor monitoring

---

## 📊 Vision Tasks

### Scene Understanding
```python
# Wat gebeurt er?
monitor.analyze_snapshot(
    "Camera1",
    "Beschrijf de activiteit in deze ruimte"
)
```

### Safety Check
```python
# Veiligheid check
monitor.analyze_snapshot(
    "Voordeur",
    "Is er iets ongebruikelijks of verdachts?"
)
```

### Inventory Check
```python
# Object inventaris
monitor.analyze_snapshot(
    "Magazijn",
    "Welke dozen zijn zichtbaar? Tel ze."
)
```

### Activity Monitoring
```python
# Monitoring
monitor.analyze_snapshot(
    "Werkplek",
    "Hoeveel mensen zijn aan het werken?"
)
```

---

## 🚨 Event System

### Event Types
- `MOTION` - Beweging gedetecteerd
- `PERSON_DETECTED` - Persoon in beeld
- `OBJECT_DETECTED` - Specifiek object gevonden
- `UNUSUAL_ACTIVITY` - Ongebruikelijk gedrag
- `INTRUSION` - Mogelijke inbraak
- `CUSTOM` - Custom events

### Event Handling
```python
from modules.vision_monitor import EventType

# Filter events
motion_events = monitor.get_events(
    event_type=EventType.MOTION,
    camera_name="Voordeur",
    limit=10
)

# Save events
monitor.save_events("events_log.json")
```

---

## 🌐 Multi-Camera Setup

### Meerdere EZVIZ Cameras
```python
from modules.ezviz_integration import get_ezviz_manager

manager = get_ezviz_manager()

# Voeg cameras toe
manager.add_husky_air("Woonkamer", "192.168.1.100", "pass1")
manager.add_husky_air("Voordeur", "192.168.1.101", "pass2")
manager.add_husky_air("Tuin", "192.168.1.102", "pass3")

# Start allemaal
manager.start_all(stream="sub")
```

### Mixed Cameras
```python
from modules.camera_monitor import CameraConfig, CameraType

# EZVIZ + Webcam + IP camera mix
cameras = [
    # EZVIZ
    ("Woonkamer", "rtsp://..."),

    # Webcam
    CameraConfig("USB_Cam", CameraType.WEBCAM, "0"),

    # Andere IP camera
    CameraConfig("Other", CameraType.RTSP, "rtsp://...")
]
```

---

## 🔒 Privacy & Security

### Data Storage
- **Snapshots**: Tijdelijk in `data/cache/`
- **Events**: Lokaal in `data/memory/`
- **Streams**: Niet opgeslagen (live only)

### Best Practices
✅ Gebruik sterke camera wachtwoorden
✅ Camera's op lokaal netwerk (niet publiek)
✅ Encryptie voor RTSP streams (indien mogelijk)
✅ Regelmatig events cleanup
✅ Access control op Telegram bot

### Auto-Cleanup
```python
# Wis oude snapshots
import shutil
shutil.rmtree(config.CACHE_DIR / "frame_*")

# Wis events
monitor.events = []
```

---

## 📈 Performance Tips

### Bandwidth Optimization
```python
# Gebruik sub stream voor monitoring
camera.start_stream("sub")  # 640x480, ~0.5 Mbps

# Main stream alleen voor belangrijke snapshots
snapshot = camera.get_snapshot("main")  # 1080p
```

### CPU/GPU Optimization
```python
# Pas analysis interval aan
monitor.analysis_interval = 10.0  # 10 sec ipv 5 sec

# Minder frequent motion detection
monitor.motion_threshold = 40  # Hogere threshold
```

### Multi-Camera Scaling
```python
# Stagger analysis over cameras
# Camera 1: t=0, t=10, t=20
# Camera 2: t=5, t=15, t=25
# etc.
```

---

## 🐛 Troubleshooting

### "Kan camera niet bereiken"
```bash
# Test connectie
ping 192.168.1.100

# Test RTSP
ffplay "rtsp://admin:PASS@192.168.1.100:554/h264/ch01/sub/av_stream"
```

### "RTSP timeout"
- Check firewall (port 554)
- Verify IP adres en wachtwoord
- Camera moet aangezet zijn
- Sub-stream gebruiken (stabieler)

### "Geen frames ontvangen"
- Start met sub stream (lagere resolutie)
- Check netwerk bandbreedte
- Verify RTSP URL format
- Probeer verschillende stream URLs

### "Motion detection te gevoelig"
```python
# Verhoog threshold
monitor.motion_threshold = 50  # Default: 30
```

---

## 🎯 Use Cases

### 1. **Home Security**
```python
# Monitor voordeur
monitor.start_monitoring(["Voordeur"])

# Alert bij persoon
def alert_person(event):
    if event.event_type == EventType.PERSON_DETECTED:
        # Stuur notificatie
        send_telegram_alert(event.description)

monitor.add_event_callback(alert_person)
```

### 2. **Baby Monitor**
```python
# Analyseer babykamer elke minuut
monitor.analysis_interval = 60.0

# Check of baby huilt
result = monitor.analyze_snapshot(
    "Babykamer",
    "Huilt de baby? Beweegt de baby?"
)
```

### 3. **Pet Monitoring**
```python
# Vind je huisdier
location = monitor.find_object(
    "Woonkamer",
    "de hond"
)
```

### 4. **Package Detection**
```python
# Check voor pakketjes
result = monitor.analyze_snapshot(
    "Voordeur",
    "Is er een pakket bezorgd?"
)
```

### 5. **Office Monitoring**
```python
# Tel mensen in kantoor
count = monitor.count_people("Kantoor")

# Check wie er is
presence = monitor.analyze_snapshot(
    "Kantoor",
    "Wie zijn er aanwezig?"
)
```

---

## 🔮 Advanced Features (Toekomst)

Geplande uitbreidingen:
- [ ] Video recording
- [ ] Multi-camera tracking (persoon volgen)
- [ ] Face recognition
- [ ] License plate reading
- [ ] Activity heatmaps
- [ ] Time-lapse generation
- [ ] Cloud storage integratie
- [ ] Mobile app notifications

---

## 📖 API Reference

### EZVIZCamera
```python
camera = setup_husky_air(name, ip, password)

camera.start_stream(stream="main"|"sub")
camera.stop_stream(stream)
camera.get_snapshot(stream)
camera.get_camera_info()
```

### VisionMonitor
```python
monitor = get_vision_monitor()

monitor.start_monitoring(cameras=None)
monitor.stop_monitoring()
monitor.analyze_snapshot(cam_name, query)
monitor.find_object(cam_name, object_desc)
monitor.count_people(cam_name)
monitor.detect_changes(cam_name, reference)
monitor.get_events(event_type, camera_name, limit)
```

### CameraManager
```python
manager = get_camera_manager()

manager.add_camera(config)
manager.start_camera(name)
manager.stop_camera(name)
manager.get_snapshot(name)
manager.list_cameras()
```

---

## ✨ Samenvatting

Je EZVIZ Husky Air is nu een **slimme AI camera** met:
- ✅ Real-time scene understanding
- ✅ Automatic event detection
- ✅ Object finding & tracking
- ✅ Person counting
- ✅ Telegram control
- ✅ Complete logging

**Start nu:**
```python
from modules.ezviz_integration import setup_husky_air
from modules.vision_monitor import get_vision_monitor

# Setup camera
camera = setup_husky_air("MijnCamera", "192.168.1.100", "wachtwoord")
camera.start_stream("sub")

# Start AI monitoring
monitor = get_vision_monitor()
monitor.start_monitoring()

# Klaar! AI monitort nu je camera 🎉
```

---

**PersonalAI Camera Monitoring v1.0**
Powered by RoboBrain 2.0 + OpenCV 📹🤖
