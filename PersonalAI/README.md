# 🤖 PersonalAI - Advanced Embodied AI System

**Intelligence = Vision + Reasoning + Memory + Autonomy**

Een geavanceerd embodied AI systeem gebouwd op **RoboBrain 2.0** met vision, autonomous decision-making, memory systems, en multi-modal perception voor intelligente robotica en assistive AI toepassingen.

## ✨ Core Capabilities

### 🧠 Autonomous Intelligence
- **Vision + Reasoning**: RoboBrain 2.0 integration voor spatial reasoning
- **Autonomous Brain**: 6-step decision loop (PERCEIVE→RECALL→REASON→DECIDE→ACT→REFLECT)
- **Enhanced Worker**: Multi-modal sensing met vision-based autonomous operation
- **Memory Systems**: Dual-store (short-term SQLite + long-term Qdrant)
- **Goal-Directed**: Priority-based goal queue met autonomous completion

### 📸 Vision & Spatial Reasoning
1. **General** - Visual question answering met thinking mode
2. **Pointing** - Identify specific points in images
3. **Grounding** - Object detection with bounding boxes
4. **Affordance** - Predict actionable areas for robot manipulation
5. **Trajectory** - Plan motion paths for reaching goals

### 🤖 Specialized Systems
- **Autonomous Trading**: Self-generating strategies, backtesting, MT5 integration
- **Smart Dashcam**: Incident detection, ANPR, lane departure warnings
- **Drone Simulation**: Waypoint planning, mission execution
- **Telegram Bot**: Remote control via messaging (vision, trading, dashcam)

### 💾 Memory & Learning
- **Short-term**: Last 50 entries (SQLite) - <1ms recall
- **Long-term**: Semantic search (Qdrant) - unlimited storage
- **Learning Types**: Lessons, patterns, discoveries, preferences
- **Auto-learning**: Stores successes (importance ≥8) and failures (≥7)

## 🚀 Installatie

### Vereisten
- Python 3.10 of hoger
- CUDA-compatible GPU (aanbevolen)
- ~20GB disk ruimte voor model

### Stap 1: Clone Repository
```bash
cd RoboBrain2.0/PersonalAI
```

### Stap 2: Installeer Dependencies

Eerst de hoofd RoboBrain requirements:
```bash
cd ..
pip install -r requirements.txt
```

Dan de PersonalAI specifieke requirements:
```bash
cd PersonalAI
pip install -r requirements.txt
```

### Stap 3: Configuratie

#### Optie A: Environment Variables (Aanbevolen)
```bash
# Kopieer .env.example naar .env
cp .env.example .env

# Bewerk .env en vul je Telegram bot token in
nano .env  # of je favoriete editor
```

#### Optie B: Direct in config.py
Bewerk `config.py` en pas de instellingen aan:
```python
TELEGRAM_TOKEN = "jouw_bot_token_hier"
ROBOBRAIN_MODEL = "BAAI/RoboBrain2.0-7B"  # of 3B/32B
```

### Stap 4: Telegram Bot Setup (Optioneel)

1. Open Telegram en zoek naar **@BotFather**
2. Stuur `/newbot` en volg de instructies
3. Kopieer de bot token die je krijgt
4. Plak de token in `.env` of `config.py`

---

## ⚡ Quick Start

### Unified Launcher

PersonalAI includes een unified launcher voor alle systemen:

```bash
# Enhanced autonomous worker (vision + reasoning)
python run.py enhanced

# Basic autonomous worker
python run.py worker

# Autonomous trader (paper mode - safe)
python run.py trader --paper

# Telegram bot (all capabilities)
python run.py telegram

# All systems at once
python run.py all

# Autonomous mode (worker + trader)
python run.py autonomous
```

### Python API

```python
from core.personalai import get_personalai

# Initialize PersonalAI
ai = get_personalai(
    enable_autonomous=True,
    enable_vision=True,
    enable_memory=True
)

# Vision analysis
result = ai.analyze_image("scene.jpg", "What's happening here?")

# Find objects
detection = ai.find_object("scene.jpg", "red cup")

# Start autonomous mode
ai.start_autonomous_mode(goals=[
    "Monitor environment for safety issues",
    "Learn patterns and optimize performance"
])

# Set new goal
ai.set_goal("Detect anomalies in sensor data", priority=9)

# Memory
ai.remember("Important discovery", importance=9, tags=["critical"])
memories = ai.recall("safety procedures")

# Reasoning
decision = ai.make_decision(
    options=["Action A", "Action B"],
    criteria="Safety and efficiency",
    context_image="scene.jpg"
)

# Status
status = ai.get_status()
print(f"Mode: {status['mode']}")
print(f"Success rate: {status['brain_stats']['success_rate']:.1%}")
```

---

## 💻 Detailed Usage

### Test het Systeem
```bash
python main.py test
```

### Check Systeem Status
```bash
python main.py status
```

### Start Telegram Bot
```bash
python main.py telegram
```

De bot is nu actief! Zoek je bot op Telegram en stuur `/start`

### Start Web Interface
```bash
python main.py web
```

Open je browser op: `http://127.0.0.1:7860`

## 📱 Telegram Bot Commando's

### Algemeen
- `/start` - Welkom bericht
- `/help` - Toon alle commando's
- `/info` - Systeem informatie
- `/stats` - Jouw statistieken
- `/settings` - Instellingen aanpassen
- `/clear` - Wis geheugen

### Vision Analyse
- `/analyze` - Analyseer een foto
- `/find <object>` - Vind object in foto
- `/point <beschrijving>` - Wijs punten aan
- `/grab <actie>` - Toon grijpgebieden
- `/move <doel>` - Plan beweging
- `/compare` - Vergelijk foto's

### X-ray (Educatief)
- `/xray` - Analyseer röntgenfoto
- `/anatomy <structuur>` - Vind anatomie

### Gebruik Voorbeelden

**Simpele foto analyse:**
```
[upload foto]
Caption: "Wat zie je hier?"
```

**Object vinden:**
```
/find de rode mok
[upload foto]
```

**Röntgen analyse:**
```
/xray
[upload röntgenfoto]
```

## 🌐 Web Interface

De web interface biedt:
- 📸 **Vision Tab**: Upload en analyseer afbeeldingen
- 🔬 **X-ray Tab**: Educatieve röntgen analyse
- ℹ️ **Info Tab**: Systeem informatie

### Features
- Drag & drop afbeelding upload
- Live task type selectie
- Thinking mode toggle
- Geannoteerde afbeelding output
- Voorbeeldvragen

## ⚙️ Configuratie

### Belangrijke Settings in `config.py`

```python
# Model selectie
ROBOBRAIN_MODEL = "BAAI/RoboBrain2.0-7B"  # 3B, 7B, of 32B

# Thinking mode standaard
DEFAULT_THINKING = True

# X-ray module
ENABLE_XRAY_MODULE = True

# Geheugen
MAX_CONVERSATION_HISTORY = 50
ENABLE_LONG_TERM_MEMORY = True

# Web interface
WEB_HOST = "127.0.0.1"
WEB_PORT = 7860
WEB_SHARE = False  # True voor publieke Gradio link
```

### Model Keuze

**RoboBrain2.0-3B** (Snel, geen thinking)
- Beste voor: Snelle analyses, beperkte resources
- GPU RAM: ~8GB
- Thinking: ❌

**RoboBrain2.0-7B** (Aanbevolen)
- Beste voor: Balans tussen snelheid en kwaliteit
- GPU RAM: ~16GB
- Thinking: ✅

**RoboBrain2.0-32B** (Beste kwaliteit)
- Beste voor: Hoogste nauwkeurigheid
- GPU RAM: ~40GB
- Thinking: ✅

## 📁 Project Structuur

```
PersonalAI/
├── core/
│   ├── brain.py          # RoboBrain integratie
│   └── memory.py         # Geheugen & voorkeuren
├── modules/
│   ├── vision.py         # Vision assistant
│   └── xray.py           # Röntgen analyse
├── interfaces/
│   ├── telegram_bot.py   # Telegram interface
│   └── web_app.py        # Web dashboard
├── data/
│   ├── cache/            # Tijdelijke bestanden
│   └── memory/           # Opgeslagen gesprekken
├── config.py             # Configuratie
├── main.py               # Hoofdlauncher
├── requirements.txt      # Python packages
└── README.md             # Deze file
```

---

## 📚 Documentation

### Core Documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture
  - Component diagrams
  - Decision loop flows
  - Memory architecture
  - Performance characteristics
  - Extension points
  - Best practices

- **[AUTONOMOUS.md](AUTONOMOUS.md)** - Autonomous mode guide
  - How autonomous mode works
  - Memory systems
  - Decision loop details
  - Setup and configuration
  - Examples and use cases

- **[TRADING.md](TRADING.md)** - Autonomous trading system
  - MT5 integration guide
  - Strategy generation
  - Backtesting framework
  - Risk management
  - Telegram trading commands

- **[CLAUDE.md](../CLAUDE.md)** - AI Assistant guide
  - For AI assistants working with this codebase
  - Project overview
  - Development guidelines
  - Best practices

### Quick References
- Enhanced Worker: See `core/enhanced_autonomous_worker.py`
- Autonomous Brain: See `core/autonomous_brain.py`
- Unified API: See `core/personalai.py`
- Telegram Commands: Run `/help` in bot
- Trading Commands: Run `/trader_help` in bot

---

## 🔒 Privacy & Veiligheid

### Lokale Data Opslag
- Alle gesprekken worden lokaal opgeslagen in `data/memory/`
- Afbeeldingen worden tijdelijk gecached in `data/cache/`
- Geen data wordt verstuurd naar externe servers (behalve voor model inference)

### X-ray Disclaimer
⚠️ **BELANGRIJK**: De X-ray module is **ALLEEN** voor educatieve doeleinden!
- Dit is **GEEN** medische diagnose tool
- Gebruik **NOOIT** voor behandelbeslissingen
- Raadpleeg altijd een gekwalificeerde arts

### Telegram Privacy
- Alleen jij hebt toegang (tenzij je `TELEGRAM_ALLOWED_USERS` instelt)
- Bot onthoudt je voorkeuren
- Gebruik `/clear` om geheugen te wissen

## 🛠️ Troubleshooting

### "Telegram token not found"
✅ Zet je bot token in `.env` of `config.py`

### "CUDA out of memory"
✅ Gebruik een kleiner model (3B ipv 7B)
✅ Of pas `device_map` aan in config

### "X-ray module niet beschikbaar"
✅ Check `ENABLE_XRAY_MODULE = True` in config.py

### "Gradio not installed"
✅ `pip install gradio`

### Model downloads langzaam
✅ Eerste keer duurt lang (~20GB download)
✅ Model wordt gecached voor volgende keren

## 🎯 Gebruik Cases

### 1. Dagelijkse Foto Assistent
- "Wat is dit voor plant?"
- "Lees de tekst op deze foto"
- "Hoeveel mensen zijn op deze foto?"

### 2. Robot Planning
- "Waar moet de robot grijpen om dit op te pakken?"
- "Plan een route naar het object"
- "Vind alle grijpbare oppervlakken"

### 3. Educatie
- Anatomie leren met röntgenfoto's
- Visuele scene analyse
- Object detectie oefeningen

### 4. Organisatie
- Foto's doorzoeken naar objecten
- Meerdere afbeeldingen vergelijken
- Visuele inventarisatie

## 🚧 Toekomstige Features (Roadmap)

- [ ] GPT/Claude integratie voor tekst conversaties
- [ ] Multi-user support voor Telegram
- [ ] Video analyse capabilities
- [ ] Document (PDF) verwerking
- [ ] Voice interface
- [ ] Mobile app
- [ ] API endpoints
- [ ] Docker container
- [ ] Cloud deployment opties

## 🤝 Contributing

Suggesties en verbeteringen zijn welkom! Open een issue of pull request.

## 📄 Licentie

Zie hoofdproject LICENSE file.

## 🙏 Credits

- **RoboBrain 2.0**: BAAI Team
- **Qwen2.5-VL**: Alibaba Qwen Team
- **python-telegram-bot**: python-telegram-bot Team
- **Gradio**: Gradio Team

## 📞 Support

Vragen of problemen?
1. Check deze README
2. Check `main.py status` voor systeem info
3. Check `main.py test` voor diagnostics
4. Zie hoofdproject documentatie

---

**Gemaakt met ❤️ voor jouw persoonlijke AI ervaring**

Veel plezier met je PersonalAI assistent! 🚀
