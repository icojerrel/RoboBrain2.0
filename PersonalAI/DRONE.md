# 🚁 PersonalAI Drone Simulator

**Vision-based Autonomous Drone Control**

Veilig testen van drone autonomous control met RoboBrain 2.0 vision AI!

---

## 🎯 Wat is Dit?

Een realistische drone simulator met **vision-based autonomous control**:

- 🚁 **Drone Physics** - Realistische vlucht simulatie
- 👁️ **Vision AI** - RoboBrain 2.0 voor scene understanding
- 🤖 **Autonomous Control** - Zelfstandige navigatie en object tracking
- 🗺️ **Path Planning** - Obstacle avoidance en waypoint navigatie
- 📊 **Telemetrie** - Volledige flight data logging

**Volledig VEILIG** - test alles virtueel voordat je een echte drone bestuurt!

---

## ⚡ Quick Start

### Simpele Test Vlucht

```python
from modules.drone_sim import get_drone_simulator, Position

# Maak drone
drone = get_drone_simulator()

# Basis vlucht
drone.arm()
drone.takeoff(altitude=15.0)
drone.move_to(Position(70, 70, 15))
drone.land()
drone.disarm()

# Render wereld
drone.render_world("flight.png")
```

### Met Vision Control

```python
from modules.drone_vision import get_drone_vision

# Maak vision controller
vision = get_drone_vision()

# Autonome vlucht naar locatie
target = Position(50, 80, 10)
vision.autonomous_flight_to(target)

# Track object met camera
vision.track_object("camera_view.jpg", "rode auto")

# Emergency landing met vision
vision.emergency_land("camera_view.jpg")
```

---

## 🎮 Telegram Bot Commands

PersonalAI Telegram bot heeft volledige drone control!

### Basic Commands

```
/drone_status          - Huidige drone status
/drone_arm             - Klaar maken voor vlucht
/drone_takeoff [alt]   - Opstijgen (default 15m)
/drone_land            - Landen
/drone_emergency       - NOODLANDING
```

### Navigation

```
/drone_goto <x> <y> [z]      - Vlieg naar positie
/drone_waypoint <x> <y> [z]  - Voeg waypoint toe
/drone_mission               - Voer alle waypoints uit
/drone_clear                 - Wis waypoints
```

### Vision Control

```
/drone_vision        - Analyseer camera (stuur foto!)
/drone_track <obj>   - Track object (stuur foto!)
/drone_landing       - Vind landing zone (stuur foto!)
/drone_auto <x> <y>  - Autonome vlucht
```

### Voorbeelden

**Simpele vlucht:**
```
/drone_arm
/drone_takeoff 20
/drone_goto 50 50 20
/drone_land
```

**Missie met waypoints:**
```
/drone_waypoint 30 30 15
/drone_waypoint 70 70 15
/drone_waypoint 50 50 15
/drone_arm
/drone_takeoff 15
/drone_mission
/drone_land
```

**Vision-based tracking:**
```
[Upload aerial photo]
/drone_track rode auto
```

---

## 🏗️ Architectuur

### Modules

#### 1. **drone_sim.py** - Drone Simulator
- Realistische vlucht physics
- Battery management
- Obstacle collision detection
- Waypoint navigation
- Telemetrie logging
- World rendering

**Key Features:**
- DJI-achtige specs (max 15 m/s, 50m altitude)
- Safety boundaries
- Emergency stop
- Battery drain simulatie

#### 2. **drone_vision.py** - Vision Controller
- RoboBrain 2.0 integratie
- Scene analysis vanuit de lucht
- Object detection & tracking
- Landing zone identification
- Obstacle detection
- Autonomous path planning

**Vision Capabilities:**
- Aerial scene understanding
- Safe landing zone detection
- Object tracking from above
- Obstacle avoidance
- Target search & approach

#### 3. **drone_interface.py** - User Interface
- Telegram command handlers
- Web interface bindings
- Status formatting
- Command parsing

---

## 🔧 Technische Details

### Drone Specs (Simulator)

```python
max_speed = 15.0 m/s              # Horizontaal
max_vertical_speed = 5.0 m/s      # Verticaal
max_altitude = 50.0 m             # Hoogte limiet
battery = 100%                    # Start capacity
battery_drain = 0.1% per seconde  # Hovering
```

### World Parameters

```python
world_size = (100, 100) meters    # Vlieg gebied
default_obstacles = 5             # Trees, buildings, etc.
safety_distance = 2.0 meters      # Min afstand tot obstakels
```

### Coordinate System

```
     Y (North)
     ^
     |
     |
     +-----> X (East)
    /
   /
  Z (Up - Altitude)

Origin: (0, 0, 0) = Grond, SW corner
```

---

## 📊 Vision Tasks

### 1. Scene Analysis
```python
vision.analyze_scene("aerial_view.jpg")
```
**Output:**
- Landschap type (bos/stad/open veld)
- Zichtbare landmarks
- Obstakels en gevaren
- Veilige routes
- Landing zones

### 2. Object Tracking
```python
vision.track_object("camera_view.jpg", "rode auto")
```
**Output:**
- Object locatie (bounding box)
- Tracking confidence
- Movement prediction

### 3. Landing Zone Detection
```python
vision.find_landing_zone("aerial.jpg")
```
**Output:**
- Safe landing areas
- Obstakel-vrije zones
- Surface quality assessment

### 4. Obstacle Detection
```python
vision.detect_obstacles("aerial.jpg")
```
**Output:**
- Alle gedetecteerde obstakels
- Posities en groottes
- Gevaar levels

---

## 🎓 Use Cases

### 1. **Training & Education**
- Leer drone besturing veilig
- Oefen emergency procedures
- Test verschillende scenario's

### 2. **Algorithm Development**
- Test path planning algorithms
- Ontwikkel vision-based control
- Evalueer autonomous behaviors

### 3. **Research**
- Aerial scene understanding
- Object tracking from drones
- Safe landing research

### 4. **Demo & Prototype**
- Demonstreer concepts
- Test voor echte drone deployment
- Valideer vision algorithms

---

## 📸 Camera Views

De simulator accepteert externe camera afbeeldingen voor vision processing:

**Supported:**
- Aerial photos (top-down)
- Perspective views
- Multi-angle shots

**Vision Processing:**
- RoboBrain 2.0 analysis
- Object detection
- Scene understanding
- Spatial reasoning

---

## 🚨 Safety Features

### Automatic Safety

✅ **Boundary Enforcement** - Blijft binnen wereld grenzen
✅ **Obstacle Avoidance** - Detecteert en vermijdt obstakels
✅ **Low Battery Landing** - Auto-land bij <20% battery
✅ **Emergency Stop** - Onmiddellijke hover en landing
✅ **Collision Detection** - Path safety checks

### Manual Safety

```python
drone.emergency_stop = True   # Activeer emergency
vision.emergency_land()       # Vision-based noodlanding
```

---

## 📈 Telemetrie & Logging

### Telemetry Data

```json
{
  "time": 12.5,
  "position": {"x": 50.2, "y": 45.8, "z": 15.0},
  "velocity": 3.2,
  "battery": 87.4,
  "state": "flying"
}
```

### Save Telemetry

```python
drone.save_telemetry("mission_log.json")
```

### Visualisatie

```python
# Render top-down wereld view
drone.render_world("world_view.png")

# Shows:
# - Drone positie en richting
# - Obstakels en safety zones
# - Waypoints
# - Real-time status
```

---

## 🔮 Toekomstige Features (Roadmap)

**Simulator Uitbreidingen:**
- [ ] Wind simulatie
- [ ] Meerdere drones (swarm)
- [ ] 3D rendering (niet alleen top-down)
- [ ] Weereffecten (regen, mist)
- [ ] Dag/nacht cyclus

**Vision Uitbreidingen:**
- [ ] Real-time video stream processing
- [ ] Multi-drone coordination
- [ ] Advanced path planning (A*, RRT)
- [ ] Semantic mapping
- [ ] SLAM integration

**Hardware Integratie:**
- [ ] DJI drone support (echte hardware!)
- [ ] Parrot bebop support
- [ ] Pixhawk/ArduPilot integratie
- [ ] FPV camera streams

---

## 🎯 Na Simulator: Echte Drone (Optie C?)

Zodra je klaar bent met de simulator, kunnen we:

### Optie C1: **DJI Integration**
- DJI Tello EDU (budget drone, €100)
- DJI SDK integratie
- Zelfde vision control, echte hardware

### Optie C2: **Custom Build**
- Pixhawk flight controller
- Raspberry Pi companion computer
- RoboBrain on-board

### Optie C3: **Advanced Features**
- Multi-drone swarm control
- Delivery missions
- Surveillance & mapping
- Search & rescue

**Welke richting wil je op? 🚁**

---

## 💡 Tips & Tricks

**Best Practices:**
1. Test altijd eerst in simulator
2. Start met lage altitude (5-10m)
3. Gebruik vision voor complexe taken
4. Monitor battery levels
5. Plan missions met safety margins

**Common Issues:**
- Battery drain te snel? → Verlaag snelheid
- Obstakels in de weg? → Gebruik vision path planning
- Mission failed? → Check telemetrie logs

---

## 📚 API Reference

### DroneSimulator

```python
drone = get_drone_simulator()

# Basic control
drone.arm()
drone.takeoff(altitude=15.0)
drone.move_to(Position(x, y, z))
drone.land()
drone.disarm()

# Waypoint missions
drone.add_waypoint(Position(x, y, z))
drone.execute_mission()

# Status & rendering
status = drone.get_status()
drone.render_world("output.png")
drone.save_telemetry("flight.json")
```

### DroneVisionController

```python
vision = get_drone_vision()

# Vision analysis
vision.analyze_scene("photo.jpg")
vision.detect_obstacles("aerial.jpg")
vision.find_landing_zone("view.jpg")

# Object tracking
vision.track_object("photo.jpg", "target")

# Autonomous control
vision.autonomous_flight_to(Position(x, y, z))
vision.emergency_land()
```

---

## 🎉 Start Experimenting!

De drone simulator is klaar voor gebruik!

```bash
# Test in Python
python PersonalAI/modules/drone_sim.py

# Test vision control
python PersonalAI/modules/drone_vision.py

# Of via Telegram bot
/drone_help
```

**Veel vliegplezier! 🚁✨**

---

**PersonalAI Drone Module v1.0**
Powered by RoboBrain 2.0 🧠
