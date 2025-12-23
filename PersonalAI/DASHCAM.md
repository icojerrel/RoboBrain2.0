# 🚗 PersonalAI Smart Dashcam

**AI-Powered Dashcam Upgrade met RoboBrain 2.0**

Transformeer je gewone dashcam naar een intelligente driving assistant met:
- 🎥 Continuous recording met event-triggered clips
- 🚨 Automatic incident detection (collision, near-miss)
- 🚗 License plate capture van omliggende voertuigen
- 🚦 Traffic sign recognition
- 🛣️ Lane departure warnings
- ⚠️ Forward collision warnings
- 😴 Driver drowsiness detection
- 📱 Distraction monitoring
- 🅿️ Parking mode surveillance
- 📍 GPS tracking met speed logging

---

## 🎯 Wat maakt dit anders dan een normale dashcam?

### Normale Dashcam:
- ✅ Video recording
- ❌ Weet niet wat het ziet
- ❌ Alleen handmatig clips opslaan
- ❌ Geen analyse van gevaarlijke situaties
- ❌ Geen verkeersbord herkenning

### PersonalAI Smart Dashcam:
- ✅ Video recording
- ✅ **Begrijpt de scene** (RoboBrain AI)
- ✅ **Automatische event detection**
- ✅ **Realtime safety warnings**
- ✅ **Traffic sign recognition**
- ✅ **License plate logging van alle voertuigen**
- ✅ **Driver monitoring** (drowsiness, distraction)
- ✅ **Intelligent clip saving** (alleen belangrijke momenten)
- ✅ **GPS + speed tracking**

---

## 🚀 Quick Start

### Basis Setup (Webcam als Dashcam)

```python
from modules.dashcam_ai import get_dashcam, RecordingMode

# Initialize met webcam
dashcam = get_dashcam(front_camera="0")

# Start continuous recording + AI monitoring
dashcam.start_recording(RecordingMode.CONTINUOUS)

# Klaar! AI monitort nu je rit en slaat automatisch events op
```

### Multi-Camera Setup (Front + Rear + Driver)

```python
dashcam = get_dashcam(
    front_camera="0",                    # Webcam 0
    rear_camera="rtsp://192.168.1.100",  # EZVIZ rear camera
    driver_camera="1"                    # Webcam 1 (driver-facing)
)

dashcam.start_recording(RecordingMode.CONTINUOUS)
```

### Met GPS Tracking

```python
# Update GPS data (from external GPS device)
dashcam.update_gps(
    latitude=52.3676,
    longitude=4.9041,
    speed=50.0,  # km/h
    heading=90.0  # degrees
)

# GPS data wordt nu gelogd bij events
```

---

## 🎯 Features in Detail

### 1. **Automatic Incident Detection**

AI detecteert automatisch gevaarlijke situaties:

```python
# Events die automatisch gedetecteerd worden:
- COLLISION: Botsing gedetecteerd
- NEAR_MISS: Bijna-botsing
- HARD_BRAKE: Harde remming
- TRAFFIC_VIOLATION: Mogelijk verkeersovertred
- FORWARD_COLLISION_WARNING: Te dichtbij voertuig vooruit
```

**Voorbeeld:**
```python
def on_incident(event):
    if event.severity == "critical":
        # Stuur alert naar telefoon
        send_telegram_alert(f"⚠️ INCIDENT: {event.description}")

        # Save video clip is al automatisch gedaan
        print(f"Clip opgeslagen: {event.video_clip_path}")

dashcam.add_event_callback(on_incident)
```

### 2. **License Plate Recognition (ANPR)**

Alle kentekens in je omgeving worden automatisch gedetecteerd:

```python
# ANPR gebeurt automatisch tijdens monitoring
# Events worden gelogd:

events = dashcam.get_events(event_type=EventType.LICENSE_PLATE_DETECTED)

for event in events:
    print(f"Kenteken: {event.metadata['plate']}")
    print(f"Tijd: {event.timestamp}")
    print(f"Locatie: {event.location}")
    print(f"Snapshot: {event.snapshot_path}")
```

**Use Cases:**
- **Hit-and-run**: Kenteken van vluchtende auto
- **Parking incidents**: Auto die jouw auto raakt
- **Tracking**: Welke auto's reden om je heen tijdens incident

**Whitelist/Blacklist:**
```python
from modules.license_plate_ai import get_license_plate_ai

lp_ai = get_license_plate_ai()

# Eigen auto's whitelisten
lp_ai.add_to_whitelist("AB-12-CD", "Mijn auto")
lp_ai.add_to_whitelist("XY-34-ZZ", "Partner's auto")

# Verdachte voertuigen blacklisten
lp_ai.add_to_blacklist("XX-99-XX", "Verdacht voertuig bij inbraak")

# Bij detectie krijg je status:
# event.metadata['plate_status'] = "whitelist" | "blacklist" | "unknown"
```

### 3. **Traffic Sign Recognition**

Verkeersborden worden gedetecteerd en gelogd:

```python
signs = dashcam.get_events(event_type=EventType.TRAFFIC_SIGN)

for sign in signs:
    print(f"Bord: {sign.description}")
    # Bijv: "Snelheidslimiet 50 km/h"
```

**Features:**
- Speed limit signs
- Stop signs
- Yield signs
- No entry signs
- School zones
- Construction zones

### 4. **Driver Monitoring** 😴

Driver-facing camera monitort:

```python
# Setup met driver camera
dashcam = get_dashcam(
    front_camera="0",
    driver_camera="1"  # Webcam naar bestuurder gericht
)

# AI checkt elke 5 seconden:
# - Zijn ogen open?
# - Kijkt naar de weg?
# - Tekenen van vermoeidheid?
# - Telefoon gebruik?

# Bij detectie:
events = dashcam.get_events(event_type=EventType.DRIVER_DROWSY)
# → "⚠️ WAARSCHUWING: Bestuurder lijkt vermoeid!"
```

**Safety Alerts:**
- `DRIVER_DROWSY`: Ogen dicht, gapen, etc.
- `DRIVER_DISTRACTED`: Telefoon, niet naar weg kijken

### 5. **Lane Departure Warning**

AI detecteert wanneer je uit je rijstrook gaat:

```python
lane_events = dashcam.get_events(event_type=EventType.LANE_DEPARTURE)

for event in lane_events:
    print(f"⚠️ Lane departure: {event.description}")
    print(f"Snapshot: {event.snapshot_path}")
```

### 6. **Forward Collision Warning**

Detecteert wanneer je te dicht op voertuig vooruit zit:

```python
fcw_events = dashcam.get_events(event_type=EventType.FORWARD_COLLISION_WARNING)
# → "Voertuig te dichtbij - verhoog afstand"
```

### 7. **Parking Mode** 🅿️

Surveillance mode wanneer auto geparkeerd is:

```python
# Activeer parking mode
dashcam.start_recording(RecordingMode.PARKING)

# In parking mode:
# - Motion detection actief
# - Lage power consumption
# - Alleen opname bij beweging
# - ANPR van passerende voertuigen

# Event bij beweging:
parking_events = dashcam.get_events(event_type=EventType.PARKING_MOTION)
```

---

## 📊 Event System

### Event Types

```python
from modules.dashcam_ai import EventType

EventType.COLLISION              # Botsing
EventType.NEAR_MISS              # Bijna-botsing
EventType.HARD_BRAKE             # Harde remming
EventType.TRAFFIC_SIGN           # Verkeersbord
EventType.LANE_DEPARTURE         # Uit rijstrook
EventType.FORWARD_COLLISION_WARNING  # Te dichtbij
EventType.DRIVER_DROWSY          # Vermoeidheid
EventType.DRIVER_DISTRACTED      # Afleiding
EventType.PARKING_MOTION         # Beweging tijdens parkeren
EventType.LICENSE_PLATE_DETECTED # Kenteken gedetecteerd
```

### Event Severity Levels

```python
"low"      # Info (bijv. verkeersbord)
"medium"   # Waarschuwing (bijv. te dichtbij)
"high"     # Belangrijk (bijv. lane departure)
"critical" # Kritiek (bijv. collision, drowsy driver)
```

### Event Callbacks

```python
def on_event(event):
    """Custom event handler"""

    # Critical events
    if event.severity == "critical":
        send_telegram_alert(event.description)
        play_audio_warning()

    # License plates
    if event.event_type == EventType.LICENSE_PLATE_DETECTED:
        plate = event.metadata['plate']
        log_to_database(plate, event.timestamp, event.location)

    # Collisions
    if event.event_type == EventType.COLLISION:
        # Video clip is automatisch opgeslagen
        upload_to_cloud(event.video_clip_path)
        notify_emergency_contact()

dashcam.add_event_callback(on_event)
```

---

## 🎬 Recording Modes

### 1. Continuous Mode

```python
dashcam.start_recording(RecordingMode.CONTINUOUS)

# - Continuous video recording
# - AI analyseert elke 2 seconden
# - Bij event: clip van 30 sec voor + 10 sec na
# - Circular buffer (overschrijft oude data)
```

### 2. Event-Only Mode

```python
dashcam.start_recording(RecordingMode.EVENT_ONLY)

# - Geen continuous recording
# - Alleen opname bij gedetecteerd event
# - Bespaart opslag
```

### 3. Parking Mode

```python
dashcam.start_recording(RecordingMode.PARKING)

# - Motion detection
# - Opname alleen bij beweging
# - Lage power voor 24/7 surveillance
```

### 4. Monitoring Only (Geen Opname)

```python
dashcam.start_monitoring()

# - AI monitoring zonder video opslaan
# - Events worden wel gelogd
# - Snapshots bij belangrijke events
# - Voor testing of privacy
```

---

## 📍 GPS Integration

### Met Externe GPS Device

```python
import serial
import pynmea2

# GPS device via serial
ser = serial.Serial('/dev/ttyUSB0', 9600)

while True:
    line = ser.readline().decode('ascii', errors='replace')

    if line.startswith('$GPRMC'):
        msg = pynmea2.parse(line)

        dashcam.update_gps(
            latitude=msg.latitude,
            longitude=msg.longitude,
            speed=msg.spd_over_grnd * 1.852,  # knots to km/h
            heading=msg.true_course
        )
```

### Met Smartphone GPS (via Bluetooth/WiFi)

```python
# Ontvang GPS data van smartphone app
def on_gps_update(data):
    dashcam.update_gps(
        latitude=data['lat'],
        longitude=data['lon'],
        speed=data['speed'],
        heading=data['heading']
    )
```

### Simulated GPS (voor testing)

```python
# Test GPS zonder hardware
dashcam.update_gps(
    latitude=52.3676,
    longitude=4.9041,
    speed=50.0,
    heading=90.0
)
```

---

## 💾 Data Management

### Event Logging

```python
# Krijg events
events = dashcam.get_events(limit=50)

# Filter op type
collisions = dashcam.get_events(event_type=EventType.COLLISION)

# Filter op severity
critical = dashcam.get_events(severity="critical")
```

### Export Events

```python
# Export naar CSV
dashcam.export_events("incidents_2024.csv", format="csv")

# Export naar JSON
dashcam.export_events("incidents_2024.json", format="json")
```

**CSV Format:**
```csv
timestamp,event_type,severity,description,confidence,speed,location,clip_path
2024-01-15T14:30:22,collision,critical,Mogelijk botsing gedetecteerd,0.85,45.2,"{'lat': 52.36, 'lon': 4.90}",/clips/collision_123.mp4
```

### Storage Paths

```
PersonalAI/data/dashcam/
├── clips/              # Video clips van events
│   ├── collision_*.mp4
│   ├── near_miss_*.mp4
│   └── ...
├── snapshots/          # Snapshots
│   ├── traffic_sign_*.jpg
│   ├── license_plate_*.jpg
│   └── ...
└── events.json         # Event database
```

### Storage Management

```python
# Auto-cleanup oude clips (> 30 dagen)
import shutil
from datetime import datetime, timedelta

def cleanup_old_clips(days=30):
    cutoff = datetime.now() - timedelta(days=days)

    for clip in dashcam.clips_dir.glob("*.mp4"):
        if datetime.fromtimestamp(clip.stat().st_mtime) < cutoff:
            clip.unlink()
            print(f"Deleted: {clip}")
```

---

## 📊 Statistics & Reports

### Real-time Stats

```python
stats = dashcam.get_statistics()

print(f"Total Events: {stats['total_events']}")
print(f"Recording: {stats['is_recording']}")
print(f"GPS Enabled: {stats['gps_enabled']}")

# Events per type
for event_type, count in stats['events_by_type'].items():
    print(f"  {event_type}: {count}")

# Events per severity
for severity, count in stats['events_by_severity'].items():
    print(f"  {severity}: {count}")
```

### Trip Summary

```python
def generate_trip_summary(start_time, end_time):
    """Generate trip report"""

    events = [e for e in dashcam.events
              if start_time <= e.timestamp <= end_time]

    print(f"📊 Trip Summary")
    print(f"Duration: {end_time - start_time}")
    print(f"Total Events: {len(events)}")

    # Safety score
    critical_count = sum(1 for e in events if e.severity == "critical")
    safety_score = max(0, 100 - (critical_count * 20))
    print(f"Safety Score: {safety_score}/100")

    # License plates logged
    plates = [e for e in events if e.event_type == EventType.LICENSE_PLATE_DETECTED]
    print(f"Vehicles logged: {len(plates)}")
```

---

## 🔧 Configuration

### config.py toevoegen:

```python
# Dashcam Settings
DASHCAM_ENABLED = True
DASHCAM_ANALYSIS_INTERVAL = 2.0  # Seconds between AI analysis
DASHCAM_BUFFER_DURATION = 30     # Seconds before event
DASHCAM_CLIP_DURATION_AFTER = 10 # Seconds after event
DASHCAM_DRIVER_CHECK_INTERVAL = 5.0  # Driver monitoring frequency

# Event Settings
DASHCAM_AUTO_SAVE_CRITICAL = True
DASHCAM_AUTO_SAVE_HIGH = True
DASHCAM_AUTO_SAVE_MEDIUM = False

# Storage
DASHCAM_MAX_STORAGE_GB = 50
DASHCAM_AUTO_CLEANUP_DAYS = 30
```

---

## 🚗 Hardware Setup Examples

### Optie 1: Webcam als Dashcam (Budget)

```python
# Gewone USB webcam op windshield
dashcam = get_dashcam(front_camera="0")
```

**Pro's:**
- ✅ Goedkoop ($20-50)
- ✅ Plug & play
- ✅ AI features werken volledig

**Con's:**
- ❌ Geen GPS (tenzij apart gekocht)
- ❌ Geen G-sensor
- ❌ Losse laptop/PC nodig

### Optie 2: EZVIZ Camera als Dashcam (Upgrade)

```python
# EZVIZ Husky Air via RTSP
dashcam = get_dashcam(
    front_camera="rtsp://admin:PASSWORD@192.168.1.100:554/h264/ch01/main/av_stream"
)
```

**Pro's:**
- ✅ Betere video kwaliteit
- ✅ WiFi streaming
- ✅ Nachtzicht
- ✅ Kan ook thuis gebruiken

**Con's:**
- ❌ WiFi hotspot in auto nodig
- ❌ Grotere power consumption

### Optie 3: Multi-Camera Pro Setup

```python
dashcam = get_dashcam(
    front_camera="0",           # 1080p dashcam
    rear_camera="1",            # Rear camera
    driver_camera="2"           # Driver monitoring
)
```

**Pro's:**
- ✅ 360° coverage
- ✅ Driver monitoring
- ✅ Complete surveillance

**Con's:**
- ❌ Duurder
- ❌ Meer power/processing

### Optie 4: Raspberry Pi Dashcam (Standalone)

```python
# Raspberry Pi 4 + Camera Module
# Compact, dedicated dashcam computer

# hardware:
# - Raspberry Pi 4 (4GB RAM)
# - Pi Camera Module v2 (front)
# - USB GPS dongle
# - Power bank / car adapter

dashcam = get_dashcam(front_camera="0")
dashcam.start_recording(RecordingMode.CONTINUOUS)
```

---

## 🎯 Use Cases

### 1. **Insurance Claims**

```python
# Bij ongeval:
collision_events = dashcam.get_events(
    event_type=EventType.COLLISION,
    severity="critical"
)

for event in collision_events:
    print(f"Time: {event.timestamp}")
    print(f"Video: {event.video_clip_path}")
    print(f"Location: {event.location}")
    print(f"Speed: {event.speed} km/h")

    # AI beschrijving van wat er gebeurde
    print(f"AI Analysis: {event.description}")

    # Kentekens van betrokken voertuigen
    nearby_plates = get_plates_near_time(event.timestamp)
```

### 2. **Traffic Violation Defense**

```python
# Bewijs snelheidslimiet
signs = dashcam.get_events(event_type=EventType.TRAFFIC_SIGN)

# Laatste snelheidsbord voor incident
last_sign = [s for s in signs if s.timestamp < incident_time][-1]
print(f"Snelheidslimiet: {last_sign.description}")
```

### 3. **Theft/Vandalism (Parking Mode)**

```python
# Activeer parking surveillance
dashcam.start_recording(RecordingMode.PARKING)

# Bij beweging tijdens parkeren:
motion_events = dashcam.get_events(event_type=EventType.PARKING_MOTION)

for event in motion_events:
    # Snapshot van persoon/voertuig
    print(f"Motion detected: {event.snapshot_path}")

    # Eventueel kenteken
    if event.metadata and 'plate' in event.metadata:
        print(f"Vehicle: {event.metadata['plate']}")
```

### 4. **Fleet Management**

```python
# Voor meerdere voertuigen:
# - Driver behavior monitoring
# - Safety scores
# - Incident tracking
# - Route optimization

def weekly_driver_report(driver_id):
    events = get_driver_events(driver_id, last_week)

    drowsy_count = len([e for e in events if e.event_type == EventType.DRIVER_DROWSY])
    distracted_count = len([e for e in events if e.event_type == EventType.DRIVER_DISTRACTED])
    harsh_brakes = len([e for e in events if e.event_type == EventType.HARD_BRAKE])

    safety_score = calculate_safety_score(events)

    return {
        'driver_id': driver_id,
        'safety_score': safety_score,
        'drowsy_incidents': drowsy_count,
        'distraction_incidents': distracted_count,
        'harsh_braking': harsh_brakes
    }
```

### 5. **Hit-and-Run Evidence**

```python
# Na hit-and-run incident:
incident_time = datetime(2024, 1, 15, 14, 30)

# Vind alle kentekens rond die tijd
plates_near_incident = [
    e for e in dashcam.get_events(EventType.LICENSE_PLATE_DETECTED)
    if abs((e.timestamp - incident_time).total_seconds()) < 60
]

for plate_event in plates_near_incident:
    print(f"Mogelijk voertuig: {plate_event.metadata['plate']}")
    print(f"Snapshot: {plate_event.snapshot_path}")
    print(f"Time: {plate_event.timestamp}")
```

---

## 🔮 Advanced Features

### Custom Event Detection

```python
def custom_analysis(frame):
    """Custom scene analysis"""

    # Bijvoorbeeld: detect school zones
    result = dashcam.brain.analyze(
        image=frame_path,
        prompt="Is this a school zone? Are there children visible?",
        task="general"
    )

    if "school" in result['answer'].lower():
        dashcam._trigger_event(
            EventType.CUSTOM,
            "School zone detected - reduce speed",
            severity="medium",
            confidence=0.7,
            metadata={'zone_type': 'school'}
        )

# Hook into analysis loop
# (would need modification to dashcam_ai.py)
```

### Integration met Telegram Bot

```python
# PersonalAI/interfaces/telegram_bot.py

def cmd_dashcam_status(update, context):
    """Get dashcam status"""
    from modules.dashcam_ai import get_dashcam

    dashcam = get_dashcam()
    stats = dashcam.get_statistics()

    message = f"🚗 Dashcam Status\\n\\n"
    message += f"Recording: {'✅' if stats['is_recording'] else '❌'}\\n"
    message += f"GPS: {'✅' if stats['gps_enabled'] else '❌'}\\n"
    message += f"Total Events: {stats['total_events']}\\n"

    update.message.reply_text(message)

def cmd_dashcam_incidents(update, context):
    """Get recent incidents"""
    from modules.dashcam_ai import get_dashcam, EventType

    dashcam = get_dashcam()

    critical = dashcam.get_events(severity="critical", limit=5)

    if not critical:
        update.message.reply_text("✅ Geen recente incidenten")
        return

    message = "🚨 Recente Incidenten:\\n\\n"
    for event in critical:
        message += f"• {event.timestamp.strftime('%H:%M')} - {event.description}\\n"

        if event.video_clip_path:
            # Stuur video clip
            context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=open(event.video_clip_path, 'rb'),
                caption=f"{event.event_type.value} - {event.description}"
            )

    update.message.reply_text(message)
```

---

## 📱 Mobile App Integration (Toekomst)

Geplande features voor mobile app:
- [ ] Live view streaming naar telefoon
- [ ] Real-time event notifications
- [ ] Remote access tot clips
- [ ] GPS tracking op kaart
- [ ] Trip playback met events overlay
- [ ] Safety score tracking
- [ ] Cloud backup van belangrijke clips

---

## ✨ Samenvatting

Je upgrade van normale dashcam naar **AI-Powered Smart Dashcam**:

**Hergebruikte PersonalAI Componenten:**
- ✅ **RoboBrain Vision AI** - Scene understanding
- ✅ **License Plate AI (ANPR)** - Kenteken herkenning
- ✅ **Face Recognition** - Driver monitoring
- ✅ **Camera Monitoring** - Multi-camera support
- ✅ **Event System** - Gestructureerde logging

**Nieuwe Dashcam Features:**
- ✅ Continuous recording met circular buffer
- ✅ Event-triggered clip saving
- ✅ GPS tracking
- ✅ Parking mode surveillance
- ✅ Driver drowsiness detection
- ✅ Traffic sign recognition
- ✅ Lane departure warnings
- ✅ Forward collision warnings

**Quick Start:**
```python
from modules.dashcam_ai import get_dashcam, RecordingMode

# Setup
dashcam = get_dashcam(front_camera="0")

# Start
dashcam.start_recording(RecordingMode.CONTINUOUS)

# Events komen automatisch binnen!
```

---

**PersonalAI Smart Dashcam v1.0**
Powered by RoboBrain 2.0 🚗🤖
