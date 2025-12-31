# PersonalAI Architecture Documentation

## System Overview

PersonalAI is an advanced embodied AI system that integrates vision, reasoning, memory, and autonomous decision-making for intelligent robotic and assistive AI applications.

### Core Philosophy

**Intelligence = Vision + Reasoning + Memory + Autonomy**

PersonalAI combines:
- **RoboBrain 2.0** for vision and spatial reasoning
- **Autonomous Brain** for intelligent decision-making
- **Memory Systems** for learning and knowledge retention
- **Multi-modal Perception** for environmental awareness

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        PersonalAI Core                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   Vision     │    │   Reasoning  │    │    Memory    │    │
│  │  (RoboBrain) │◄───┤    (Brain)   │◄───┤  (Dual-Store)│    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│         │                    │                    │           │
│         └────────────────────┴────────────────────┘           │
│                              │                                │
│                    ┌─────────▼─────────┐                     │
│                    │ Autonomous Brain  │                     │
│                    │ (Decision Loop)   │                     │
│                    └─────────┬─────────┘                     │
│                              │                                │
│         ┌────────────────────┼────────────────────┐          │
│         │                    │                    │          │
│  ┌──────▼──────┐    ┌────────▼────────┐    ┌────▼─────┐    │
│  │  Enhanced   │    │   Autonomous    │    │  Trading │    │
│  │   Worker    │    │   Supervisor    │    │  System  │    │
│  └─────────────┘    └─────────────────┘    └──────────┘    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
         │                      │                      │
    ┌────▼────┐           ┌────▼────┐           ┌────▼────┐
    │Telegram │           │Dashcam  │           │  Web    │
    │   Bot   │           │   AI    │           │Dashboard│
    └─────────┘           └─────────┘           └─────────┘
```

---

## Core Components

### 1. Brain (`core/brain.py`)

**Purpose:** RoboBrain 2.0 integration for vision and spatial reasoning

**Capabilities:**
- Multi-modal visual understanding (images, video)
- Spatial reasoning (pointing, grounding, affordance)
- Trajectory planning for manipulation
- Chain-of-thought reasoning (7B/32B models)

**Key Methods:**
```python
brain.analyze(image, prompt, task="general", thinking=True)
brain.find_objects(image, description, plot=True)
brain.predict_trajectory(image, goal, plot=True)
brain.get_affordance(image, action, plot=True)
```

**Task Types:**
- `general` - Visual question answering
- `pointing` - Point to specific locations
- `grounding` - Object detection with bounding boxes
- `affordance` - Predict actionable areas for robots
- `trajectory` - Plan motion paths

---

### 2. Autonomous Brain (`core/autonomous_brain.py`)

**Purpose:** Intelligent autonomous decision-making with vision+reasoning

**Decision Loop (6 steps):**

```
1. PERCEIVE  → Use vision to understand environment
2. RECALL    → Query memory for relevant knowledge
3. REASON    → Use thinking mode to analyze situation
4. DECIDE    → Choose optimal action based on reasoning
5. ACT       → Execute decision
6. REFLECT   → Learn from results
```

**Features:**
- Vision-based environmental perception
- Confidence-based decision making (0.5-0.9 scale)
- Automatic lesson storage in long-term memory
- Performance tracking and success rate monitoring
- Pattern detection every 10 cycles

**Decision Types:**
- **Autonomous** (confidence ≥0.8) - Proactive operation
- **Cautious** (confidence 0.5-0.8) - Reactive with monitoring
- **Conservative** (confidence <0.5) - Observation mode

**Usage:**
```python
brain = get_autonomous_brain()
result = brain.autonomous_decision_cycle(
    environment_image="scene.jpg",
    user_goal="Monitor for safety issues"
)
```

---

### 3. Enhanced Autonomous Worker (`core/enhanced_autonomous_worker.py`)

**Purpose:** Continuous autonomous operation with vision and multi-modal sensing

**Capabilities:**
- Vision-based environmental monitoring
- Goal-directed behavior with priority queue
- Multi-modal sensing (dashcam, camera, internal state)
- Self-improving through experience
- Multi-agent coordination

**Operation Modes:**
- **60-second cycles** (default) - Balanced operation
- **Custom intervals** - Configurable based on use case
- **Background operation** - Runs in separate thread

**Sensors:**
1. **Dashcam** - Road/driving scenarios
2. **Camera** - General environment monitoring
3. **Internal State** - System metrics and memory

**Usage:**
```python
worker = EnhancedAutonomousWorker(
    cycle_interval=60,
    enable_vision=True
)
worker.set_goal("Monitor environment for anomalies", priority=9)
worker.start()
```

---

### 4. Memory Systems (`core/autonomous_memory.py`)

**Purpose:** Dual-store memory for learning and knowledge retention

#### Short-Term Memory (SQLite)
- **Capacity:** Last 50 entries (rolling window)
- **Storage:** Local SQLite database
- **Speed:** Fast (~1ms reads)
- **Use Case:** Recent context, immediate recall

#### Long-Term Memory (Qdrant - Optional)
- **Capacity:** Unlimited (vector database)
- **Storage:** Qdrant vector store
- **Speed:** Semantic search (<100ms)
- **Use Case:** Lessons, patterns, discoveries

**Memory Types:**
- `action` - Actions taken
- `observation` - Observations made
- `thought` - Reasoning and analysis
- `goal` - Goals and objectives
- `result` - Outcomes and results
- `lesson` - Learnings (long-term)
- `pattern` - Identified patterns (long-term)
- `discovery` - Important findings (long-term)
- `preference` - User preferences

**Importance Threshold:**
- **1-4:** Short-term only
- **5-10:** Both short and long-term

**Usage:**
```python
# Store memory
remember_short("observation", "Detected anomaly in sensor data")
remember_long("lesson", "When X happens, do Y", tags=["safety"], importance=8)

# Recall memory
recent = recall_recent(limit=10)
relevant = recall_relevant("safety procedures", limit=5)
```

---

### 5. Unified PersonalAI Core (`core/personalai.py`)

**Purpose:** Central integration point for all capabilities

**Unified Interface:**
```python
from core.personalai import get_personalai

# Initialize
ai = get_personalai(
    enable_autonomous=True,
    enable_vision=True,
    enable_memory=True
)

# Vision
result = ai.analyze_image("scene.jpg", "What's happening here?")
detection = ai.find_object("scene.jpg", "red cup")

# Autonomous
ai.start_autonomous_mode(goals=["Monitor safety", "Optimize performance"])
ai.set_goal("New priority task", priority=9)

# Memory
ai.remember("Important discovery", importance=9, tags=["critical"])
memories = ai.recall("safety procedures")

# Reasoning
analysis = ai.think_about("Should I take action X?", context_image="scene.jpg")
decision = ai.make_decision(
    options=["Option A", "Option B"],
    criteria="Safety and efficiency",
    context_image="scene.jpg"
)

# Status
status = ai.get_status()
capabilities = ai.get_capabilities()
```

**Operation Modes:**
- **Manual** - User-controlled operation
- **Autonomous** - Full autonomous operation
- **Hybrid** - Mixed manual/autonomous

---

## Specialized Systems

### Autonomous Trading System

**Location:** `trading/`

**Components:**
- `autonomous_trader.py` - Main trading agent (600 lines)
- `mt5_connector.py` - MetaTrader 5 integration (500 lines)
- `strategy_generator.py` - Strategy code generation (450 lines)
- `backtester.py` - Performance testing (350 lines)
- `risk_manager.py` - Position sizing and limits (350 lines)

**Features:**
- Self-generating trading strategies
- Autonomous backtesting and optimization
- Risk management (1% per trade, 3% daily max)
- Paper trading mode for safe testing
- Learning from P&L results

**Integration:**
```python
# Via PersonalAI Core
ai.start_autonomous_mode()
ai.set_goal("Generate and test profitable trading strategy", priority=8)

# Via Telegram Bot
/trader_start paper
/trader_status
/trader_stats
```

---

### Smart Dashcam System

**Location:** `modules/dashcam_ai.py`

**Features:**
- Automatic incident detection
- License plate recognition (ANPR)
- Traffic sign detection
- Lane departure warnings
- Driver monitoring
- GPS tracking

**Integration:**
```python
# Autonomous monitoring
worker = EnhancedAutonomousWorker()
# Automatically uses dashcam if available
worker.start()

# Via Telegram
/dashcam_start
/dashcam_status
/dashcam_incidents
```

---

## Interfaces

### 1. Telegram Bot (`interfaces/telegram_bot.py`)

**Commands:**

**Vision:**
- `/analyze` - Analyze uploaded image
- `/find <object>` - Find object in image
- `/point <description>` - Point to locations

**Autonomous:**
- `/worker_status` - Check autonomous worker status
- `/set_goal <goal>` - Set new goal for worker

**Trading:**
- `/trader_start [paper|live]` - Start autonomous trader
- `/trader_status` - Trading status and P&L
- `/trader_stats` - Performance statistics

**Dashcam:**
- `/dashcam_start` - Start recording
- `/dashcam_incidents` - Critical incidents
- `/dashcam_plates` - Detected license plates

**Integration:**
```python
# Start Telegram bot
python interfaces/telegram_bot.py

# Via launcher
python run.py telegram
```

---

### 2. Web Dashboard (`interfaces/web_app.py`)

**Features:**
- Vision analysis interface
- Autonomous worker monitoring
- Memory browser
- Performance metrics
- System status

---

### 3. Unified Launcher (`run.py`)

**Modes:**
```bash
# Basic autonomous worker
python run.py worker

# Enhanced worker (vision+reasoning)
python run.py enhanced

# Autonomous trader
python run.py trader --paper

# Telegram bot
python run.py telegram

# All systems
python run.py all

# Autonomous mode (worker + trader)
python run.py autonomous
```

---

## Data Flow

### Perception → Decision → Action Flow

```
1. SENSOR INPUT
   ├─ Dashcam frame
   ├─ Camera capture
   └─ Internal metrics
         │
         ▼
2. PERCEPTION (Brain)
   ├─ Vision analysis
   ├─ Object detection
   └─ Scene understanding
         │
         ▼
3. MEMORY RECALL
   ├─ Recent context (short-term)
   └─ Relevant lessons (long-term)
         │
         ▼
4. REASONING (Autonomous Brain)
   ├─ Situation analysis
   ├─ Option evaluation
   └─ Confidence assessment
         │
         ▼
5. DECISION
   ├─ Action selection
   ├─ Parameter setting
   └─ Priority assignment
         │
         ▼
6. ACTION EXECUTION
   ├─ Worker action
   ├─ Trading order
   └─ Alert/notification
         │
         ▼
7. REFLECTION
   ├─ Result evaluation
   ├─ Lesson storage
   └─ Pattern detection
```

---

## Memory Flow

### Short-Term Memory (Immediate)
```
Action/Observation
    │
    ▼
SQLite Insert
    │
    ▼
Keep Last 50
    │
    ▼
Available for recall
```

### Long-Term Memory (Important Events)
```
Event (importance ≥ 5)
    │
    ▼
Generate embedding
    │
    ▼
Store in Qdrant
    │
    ▼
Available for semantic search
```

### Memory Lifecycle
```
┌──────────────┐
│  New Event   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Short-term   │ ←─── Always stored
│  (SQLite)    │
└──────┬───────┘
       │
       ▼ (if importance ≥ 5)
┌──────────────┐
│  Long-term   │
│  (Qdrant)    │
└──────────────┘
```

---

## Performance Characteristics

### Vision (RoboBrain)
- **Model:** 7B parameters (default)
- **Inference Time:** ~2-5 seconds per image
- **Thinking Mode:** +1-3 seconds
- **Accuracy:** State-of-the-art on embodied AI benchmarks

### Autonomous Brain
- **Decision Time:** ~3-10 seconds (with vision)
- **Decision Time:** ~0.5-1 second (without vision)
- **Success Rate:** Typically 70-90% (improves over time)
- **Learning:** Continuous, every cycle

### Memory
- **Short-term Read:** <1ms
- **Long-term Search:** <100ms
- **Storage:** Unlimited (Qdrant), 50 entries (SQLite)

### Autonomous Worker
- **Cycle Time:** 60 seconds (default, configurable)
- **Perception Time:** ~5 seconds (vision) or instant (internal)
- **Decision Time:** ~10 seconds
- **Action Time:** Variable (depends on action)

---

## Configuration

### Key Settings (`config.py`)

```python
# Model
ROBOBRAIN_MODEL = "BAAI/RoboBrain2.0-7B"  # or 3B, 32B
ROBOBRAIN_DEVICE = "auto"  # or "cuda", "cpu"

# Defaults
DEFAULT_THINKING = True  # Enable chain-of-thought
DEFAULT_TEMPERATURE = 0.7  # Sampling temperature

# Autonomous
AUTONOMOUS_CYCLE_INTERVAL = 60  # seconds
AUTONOMOUS_ENABLE_VISION = True
AUTONOMOUS_ENABLE_MEMORY = True

# Memory
MEMORY_SHORT_TERM_LIMIT = 50  # entries
MEMORY_LONG_TERM_THRESHOLD = 5  # importance
QDRANT_ENABLED = True  # Long-term memory
```

---

## Extension Points

### Adding New Capabilities

1. **New Sensor:**
```python
# In enhanced_autonomous_worker.py
def _get_new_sensor_data(self):
    # Your sensor logic
    return sensor_data
```

2. **New Action:**
```python
# In autonomous_brain.py → _act()
elif action == "new_custom_action":
    result = self._execute_custom_action()
```

3. **New Memory Type:**
```python
# Usage
remember_long(
    type="custom_type",
    content="...",
    tags=["custom"],
    importance=7
)
```

---

## Best Practices

### Memory Usage
- ✅ Store important discoveries (importance ≥ 7)
- ✅ Use descriptive tags for easy retrieval
- ✅ Store both successes and failures
- ❌ Don't store every action in long-term memory
- ❌ Don't use vague tags like "general"

### Autonomous Operation
- ✅ Set clear, specific goals
- ✅ Use priority levels appropriately (1-10)
- ✅ Monitor success rates
- ✅ Review long-term memory patterns
- ❌ Don't run live trading without testing
- ❌ Don't ignore low confidence decisions

### Vision Tasks
- ✅ Use thinking mode for complex reasoning
- ✅ Choose appropriate task type
- ✅ Enable plotting for debugging
- ❌ Don't use multi-image for pointing/affordance
- ❌ Don't skip vision preprocessing

---

## Troubleshooting

### Common Issues

**1. Vision Analysis Slow**
- Solution: Use 3B model for faster inference
- Solution: Disable thinking mode for simple queries
- Solution: Use GPU acceleration

**2. Memory Not Persisting**
- Check: Qdrant is installed and running
- Check: Importance threshold (must be ≥ 5)
- Fallback: Short-term memory always works

**3. Autonomous Worker Not Acting**
- Check: Goals are set with adequate priority
- Check: Environment image is accessible
- Check: Brain initialization succeeded

**4. Low Success Rate**
- Increase: Confidence threshold for actions
- Review: Long-term memory for failure patterns
- Adjust: Goal specificity and clarity

---

## Future Enhancements

### Planned Features
- [ ] LLM integration for text-based reasoning
- [ ] Voice interface (speech-to-text/text-to-speech)
- [ ] Multi-robot coordination
- [ ] Cloud memory sync
- [ ] Advanced pattern recognition
- [ ] Transfer learning between tasks
- [ ] Emotion recognition
- [ ] Real-time video processing

### Research Directions
- Continuous learning from human feedback
- Meta-learning for rapid task adaptation
- Hierarchical goal planning
- Multimodal fusion improvements
- Uncertainty quantification

---

## References

- **RoboBrain 2.0:** https://superrobobrain.github.io/
- **Paper:** https://arxiv.org/abs/2507.02029
- **Hugging Face:** https://huggingface.co/collections/BAAI/robobrain20-6841eeb1df55c207a4ea0036/
- **FlagScale Training:** https://github.com/FlagOpen/FlagScale
- **FlagEvalMM Evaluation:** https://github.com/flageval-baai/FlagEvalMM

---

**Last Updated:** 2025-12-31
**Version:** 2.0 (Enhanced Core with Vision+Reasoning)
