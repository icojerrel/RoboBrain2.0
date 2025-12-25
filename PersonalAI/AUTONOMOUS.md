# 🤖 PersonalAI Autonomous Mode

**Self-directed AI agent met memory systems en continuous learning**

PersonalAI kan nu **autonoom opereren** - zelfstandig beslissingen nemen, leren van ervaringen, en zich continue verbeteren zonder menselijke input.

---

## 🏗️ Architectuur

```
┌────────────────────────────────────────────────────────┐
│                    PersonalAI VM                       │
│                                                        │
│  ┌──────────────┐      ┌────────────────────┐        │
│  │  INITIATOR   │      │  SUPERVISOR        │        │
│  │  (Manual)    │      │  (systemd timer)   │        │
│  │              │      │                    │        │
│  │  - User CLI  │      │  - Health checks   │        │
│  │  - Telegram  │      │  - Interventions   │        │
│  └──────────────┘      └────────────────────┘        │
│                                                        │
│         │                       │                     │
│         │                       │ monitors            │
│         ▼                       ▼                     │
│  ┌──────────────────────────────────────────┐        │
│  │         WORKER (Autonomous)              │        │
│  │                                          │        │
│  │  Decision Loop:                          │        │
│  │  1. READ   - short-term memory           │        │
│  │  2. QUERY  - long-term memory search     │        │
│  │  3. THINK  - analyze & decide            │        │
│  │  4. ACT    - execute decision            │        │
│  │  5. RECORD - log to memory               │        │
│  │  6. LEARN  - store discoveries           │        │
│  └──────────────────────────────────────────┘        │
│                                                        │
│         │                       │                     │
│         ▼                       ▼                     │
│  ┌──────────────┐      ┌────────────────────┐        │
│  │  SHORT-TERM  │      │   LONG-TERM        │        │
│  │  MEMORY      │      │   MEMORY           │        │
│  │              │      │                    │        │
│  │  SQLite3     │      │   Qdrant           │        │
│  │  (last 50)   │      │   (vectors)        │        │
│  └──────────────┘      └────────────────────┘        │
│                                                        │
│                        ▼                              │
│               ┌─────────────────┐                     │
│               │     ACTION      │                     │
│               │                 │                     │
│               │ - Dashcam check │                     │
│               │ - Pattern learn │                     │
│               │ - Optimize      │                     │
│               │ - Self-improve  │                     │
│               └─────────────────┘                     │
└────────────────────────────────────────────────────────┘
```

---

## 🧠 Memory Systems

### **1. Short-Term Memory (SQLite)**

**Purpose:** Immediate context (last 50 entries)

**Storage:** `PersonalAI/data/memory/short_term.db`

**Types:**
- `action` - Actions taken
- `observation` - Things observed
- `thought` - Reasoning process
- `goal` - Current goals
- `result` - Action results

**Usage:**
```python
from core.autonomous_memory import remember_short, recall_recent

# Store
remember_short("action", "Checked dashcam events")
remember_short("observation", "Found 3 critical incidents")

# Retrieve
recent = recall_recent(limit=10)
for mem in recent:
    print(f"[{mem.type}] {mem.content}")
```

**Auto-cleanup:** Keeps only last 50 entries

---

### **2. Long-Term Memory (Qdrant)**

**Purpose:** Semantic search for significant learnings

**Storage:** Qdrant vector database (localhost:6333)

**Types:**
- `fact` - Important facts learned
- `skill` - Skills/capabilities mastered
- `preference` - User preferences
- `lesson` - Lessons from successes/failures
- `discovery` - New discoveries
- `pattern` - Identified patterns

**Importance:** 1-10 (only stores if ≥ 5)

**Usage:**
```python
from core.autonomous_memory import remember_long, recall_relevant

# Store significant learning
remember_long(
    type="discovery",
    content="Yi dashcam jailbreak provides best RTSP access",
    tags=["dashcam", "hardware", "jailbreak"],
    importance=8
)

# Semantic search
relevant = recall_relevant("dashcam setup", limit=5)
for mem in relevant:
    print(f"[{mem.type}] {mem.content} (importance={mem.importance})")
```

**Vector Embeddings:** Currently mock embeddings (replace with OpenAI/sentence-transformers in production)

---

## ⚙️ Decision Loop

Worker agent runs continuous **decision cycles** (every 30 seconds):

### **1. READ - Get Context**
```python
context = {
    "recent_actions": [...],
    "recent_observations": [...],
    "recent_goals": [...],
    "recent_thoughts": [...]
}
```

### **2. QUERY - Search Knowledge**
```python
# Semantic search in long-term memory
relevant_knowledge = recall_relevant(query, limit=3)
```

### **3. THINK - Decide Action**
```python
decision = {
    "action": "check_dashcam_events",
    "reasoning": "Regular monitoring cycle",
    "priority": 7
}
```

**Decision logic:**
- Check dashcam events (every cycle)
- Analyze patterns (every 10 cycles)
- Optimize performance (every 20 cycles)
- Self-improvement (default)

### **4. ACT - Execute**
```python
result = execute_action(decision)
# Returns: {"success": True/False, "message": "..."}
```

### **5. RECORD - Log**
```python
remember_short("action", f"{action}: {result}")
remember_short("observation", "Action outcome...")
```

### **6. LEARN - Store Discoveries**
```python
if result["success"] and priority >= 7:
    remember_long(
        type="lesson",
        content=f"{action} successful: {result}",
        tags=[...],
        importance=priority
    )
```

---

## 🚀 Setup & Usage

### **Prerequisites**

```bash
# Install Qdrant (long-term memory)
docker run -d -p 6333:6333 qdrant/qdrant

# Or skip Qdrant (short-term memory only)
# Worker will run but long-term learning disabled
```

### **Install Dependencies**

```bash
cd PersonalAI

# Install qdrant-client
pip install qdrant-client

# Or add to requirements.txt:
echo "qdrant-client>=1.7.0" >> requirements.txt
pip install -r requirements.txt
```

### **Manual Testing**

```bash
# Test memory systems
python core/autonomous_memory.py

# Test worker (runs continuously)
python core/autonomous_worker.py

# Test supervisor (one-shot check)
python core/autonomous_supervisor.py
```

### **Production Deployment**

```bash
# 1. Create personalai user
sudo useradd -m -s /bin/bash personalai

# 2. Copy PersonalAI to home
sudo cp -r PersonalAI /home/personalai/
sudo chown -R personalai:personalai /home/personalai/PersonalAI

# 3. Setup venv
sudo -u personalai bash -c "
    cd /home/personalai/PersonalAI
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
"

# 4. Install systemd services
sudo cp PersonalAI/systemd/personalai-worker.service /etc/systemd/system/
sudo cp PersonalAI/systemd/personalai-supervisor.service /etc/systemd/system/
sudo cp PersonalAI/systemd/personalai-supervisor.timer /etc/systemd/system/

# 5. Start services
sudo systemctl daemon-reload

# Start worker (continuous)
sudo systemctl enable personalai-worker
sudo systemctl start personalai-worker

# Start supervisor timer (checks every 5 min)
sudo systemctl enable personalai-supervisor.timer
sudo systemctl start personalai-supervisor.timer

# 6. Check status
sudo systemctl status personalai-worker
sudo systemctl status personalai-supervisor.timer

# 7. View logs
sudo journalctl -u personalai-worker -f
sudo journalctl -u personalai-supervisor -f
```

---

## 📊 Monitoring

### **Check Worker Status**

```bash
# Systemd status
sudo systemctl status personalai-worker

# Real-time logs
sudo journalctl -u personalai-worker -f

# Recent activity
sudo journalctl -u personalai-worker --since "1 hour ago"
```

### **Check Supervisor**

```bash
# Timer status
sudo systemctl status personalai-supervisor.timer

# Last check output
sudo journalctl -u personalai-supervisor -n 50

# Supervisor reports
sudo journalctl -u personalai-supervisor --since today | grep "SUPERVISOR REPORT"
```

### **Query Memory**

```python
from core.autonomous_memory import get_short_term_memory, get_long_term_memory

# Short-term
stm = get_short_term_memory()
recent = stm.get_recent(20)

# Long-term
ltm = get_long_term_memory()
discoveries = ltm.get_all(type="discovery", limit=50)
```

---

## 🎯 Autonomous Actions

Worker can autonomously perform:

### **1. Check Dashcam Events**
```
- Monitor dashcam for new events
- Detect critical incidents
- Store discoveries in long-term memory
- Trigger Telegram alerts (TODO)
```

### **2. Analyze Patterns**
```
- Review all discoveries and lessons
- Identify recurring patterns
- Store pattern insights
- Optimize based on findings
```

### **3. Optimize Performance**
```
- Analyze memory usage
- Check action/observation ratio
- Identify inefficiencies
- Store optimization recommendations
```

### **4. Self-Improvement**
```
- Review recent failures
- Learn from mistakes
- Consolidate knowledge
- Avoid repeating errors
```

---

## 🔧 Configuration

### **Worker Settings**

Edit `core/autonomous_worker.py`:

```python
# Decision cycle frequency
time.sleep(30)  # 30 seconds between cycles

# Pattern analysis frequency
return self.cycle_count % 10 == 0  # Every 10 cycles

# Optimization frequency
return self.cycle_count % 20 == 0  # Every 20 cycles
```

### **Memory Settings**

Edit `core/autonomous_memory.py`:

```python
# Short-term memory size
LIMIT 50  # Keep last 50 entries

# Long-term importance threshold
if importance < 5:  # Only store if importance >= 5
    return

# Qdrant connection
QdrantClient(host="localhost", port=6333)
```

### **Supervisor Settings**

Edit `systemd/personalai-supervisor.timer`:

```ini
# Check frequency
OnUnitActiveSec=5min  # Every 5 minutes
```

---

## 🧪 Examples

### **Example 1: Dashcam Incident Learning**

```
1. Dashcam detects collision
2. Worker checks events (decision loop)
3. Finds critical event
4. Records to short-term:
   - action: "check_dashcam_events"
   - observation: "Critical collision event detected"
5. Stores to long-term:
   - type: "discovery"
   - content: "Dashcam collision at intersection X"
   - tags: ["dashcam", "collision", "critical"]
   - importance: 9
6. Future: When checking events, recalls this pattern
   - "Intersection X has history of collisions"
```

### **Example 2: Pattern Recognition**

```
1. After 10 cycles, worker decides: "analyze_patterns"
2. Queries all discoveries and lessons
3. Finds pattern: "license_plate" tag appears 50 times
4. Stores pattern:
   - type: "pattern"
   - content: "License plate detection is most frequent activity"
   - importance: 7
5. Future: Optimizes to focus on ANPR improvements
```

### **Example 3: Self-Recovery**

```
1. Worker encounters repeated errors
2. Supervisor detects error loop (health check)
3. Triggers intervention
4. Stores lesson:
   - type: "lesson"
   - content: "API timeout - need retry logic"
   - importance: 8
5. Worker learns to avoid that approach
6. Next time: Checks long-term memory first
   - Finds lesson about timeouts
   - Uses different approach
```

---

## 🛠️ Extending Autonomous Capabilities

### **Add New Decision Type**

Edit `core/autonomous_worker.py`:

```python
def _think(self, context, knowledge):
    # Add new decision logic
    if self._should_backup_data():
        decision = {
            "action": "backup_data",
            "reasoning": "Regular backup cycle",
            "priority": 6
        }

def _should_backup_data(self):
    # Every 50 cycles
    return self.cycle_count % 50 == 0

def _act(self, decision):
    if action == "backup_data":
        result = self._backup_data()

def _backup_data(self):
    # Implementation
    ...
```

### **Add New Memory Type**

```python
remember_long(
    type="strategy",  # New type
    content="Best dashcam setup is Yi + RPi combo",
    tags=["dashcam", "hardware", "strategy"],
    importance=8
)
```

### **Custom Supervisor Checks**

Edit `core/autonomous_supervisor.py`:

```python
def _check_custom_metric(self):
    # Custom health check
    ...
    return {"status": "...", "healthy": True/False}
```

---

## 📈 Future Improvements

### **Planned Features:**

- [ ] **Real embeddings** (OpenAI API or sentence-transformers)
- [ ] **Telegram integration** for autonomous alerts
- [ ] **Multi-agent coordination** (multiple workers)
- [ ] **Goal planning** (long-term goal decomposition)
- [ ] **Reward modeling** (reinforcement learning-style)
- [ ] **Tool learning** (discover new capabilities)
- [ ] **Code generation** (autonomous skill creation)
- [ ] **Web research** (autonomous information gathering)

### **Advanced Memory:**

- [ ] **Memory consolidation** (compress old memories)
- [ ] **Importance re-ranking** (update based on usefulness)
- [ ] **Memory pruning** (remove outdated knowledge)
- [ ] **Cross-memory references** (link related memories)

### **Enhanced Decision Making:**

- [ ] **Multi-step planning** (complex goal decomposition)
- [ ] **Uncertainty quantification** (confidence scores)
- [ ] **Exploration vs exploitation** (balance learning/performance)
- [ ] **Meta-learning** (learn how to learn)

---

## ⚠️ Limitations & Warnings

### **Current Limitations:**

❌ **Mock embeddings** - Semantic search limited (use real embeddings in production)
❌ **No authentication** - Qdrant not password-protected
❌ **Single-threaded** - One decision at a time
❌ **No error recovery** - Crashes require manual restart (systemd helps)
❌ **Limited action repertoire** - Only 4 autonomous actions

### **Safety Considerations:**

⚠️ **Autonomous agent** - Can make decisions without human approval
⚠️ **Resource usage** - Runs 24/7, uses CPU/memory continuously
⚠️ **Data persistence** - Memory fills up over time (need cleanup)
⚠️ **Qdrant dependency** - Requires external database

### **Recommendations:**

✅ Monitor logs regularly (journalctl)
✅ Set resource limits (systemd MemoryLimit/CPUQuota)
✅ Backup memory databases periodically
✅ Use real embeddings for production
✅ Add authentication to Qdrant
✅ Implement proper error handling
✅ Test thoroughly before production use

---

## 🎓 Autonomous AI Concepts

### **Why Autonomous?**

Traditional AI: **Reactive**
```
User → Request → AI → Response → Done
```

Autonomous AI: **Proactive**
```
AI → Observe → Think → Act → Learn → Repeat
```

### **Key Principles:**

**1. Continuous Operation**
- Runs 24/7 in background
- No human input needed
- Self-directed decision making

**2. Memory-Based Learning**
- Short-term: Immediate context
- Long-term: Accumulated knowledge
- Semantic search: Relevant retrieval

**3. Decision Loop**
- Read context
- Query knowledge
- Think & decide
- Act on decision
- Record results
- Learn from outcomes

**4. Self-Improvement**
- Analyze failures
- Identify patterns
- Optimize strategies
- Avoid repeating mistakes

### **Comparison to Other Approaches:**

| Approach | PersonalAI | AutoGPT | LangChain Agents |
|----------|------------|---------|------------------|
| **Memory** | SQLite + Qdrant | File-based | In-memory only |
| **Deployment** | systemd service | Manual run | Application-embedded |
| **Supervision** | Dedicated supervisor | None | None |
| **Learning** | Long-term storage | Limited | Session-only |
| **Actions** | Dashcam, analysis | Web, coding | Tool-specific |

---

## 📚 Resources

### **Dependencies:**

- **Qdrant**: https://qdrant.tech/
- **SQLite3**: Built-in Python
- **RoboBrain**: PersonalAI core AI

### **Similar Projects:**

- **AutoGPT**: https://github.com/Significant-Gravitas/AutoGPT
- **BabyAGI**: https://github.com/yoheinakajima/babyagi
- **AgentGPT**: https://github.com/reworkd/AgentGPT

### **Papers:**

- *"Generative Agents: Interactive Simulacra of Human Behavior"* (Stanford, 2023)
- *"ReAct: Synergizing Reasoning and Acting in Language Models"* (Google, 2022)
- *"Reflexion: Language Agents with Verbal Reinforcement Learning"* (Northeastern, 2023)

---

## ✅ Quick Start Summary

```bash
# 1. Install Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# 2. Install dependencies
pip install qdrant-client

# 3. Test memory
python core/autonomous_memory.py

# 4. Test worker (Ctrl+C to stop)
python core/autonomous_worker.py

# 5. Test supervisor
python core/autonomous_supervisor.py

# 6. Deploy to systemd (production)
sudo systemctl enable --now personalai-worker
sudo systemctl enable --now personalai-supervisor.timer

# 7. Monitor
sudo journalctl -u personalai-worker -f
```

---

**PersonalAI Autonomous Mode v1.0**
🤖 Self-directed AI with memory and learning
