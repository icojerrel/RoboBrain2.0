"""
PersonalAI Autonomous Worker - Standalone Version

Lightweight autonomous worker zonder heavy dependencies
Voor demo/testing zonder RoboBrain
"""

import time
import logging
from datetime import datetime
from pathlib import Path
import sqlite3
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "memory" / "short_term.db"


class AutonomousWorkerStandalone:
    """Standalone autonomous worker"""

    def __init__(self):
        self.running = False
        self.cycle_count = 0

        # Ensure DB exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

        logger.info("🤖 Autonomous Worker initialized (standalone mode)")

    def _init_db(self):
        """Initialize database if needed"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

    def start(self):
        """Start autonomous operation"""
        self.running = True

        self._remember("goal", "Start autonomous operation")
        logger.info("🚀 Autonomous Worker starting...\n")

        try:
            while self.running:
                self.decision_cycle()
                self.cycle_count += 1

                # Sleep between cycles
                time.sleep(5)  # 5 second cycles for demo

        except KeyboardInterrupt:
            logger.info("\n⏸️ Autonomous Worker stopping...")
            self.running = False

        self._remember("observation", "Autonomous operation stopped")
        logger.info("🛑 Autonomous Worker stopped")

    def decision_cycle(self):
        """Single decision cycle"""

        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 DECISION CYCLE #{self.cycle_count}")
        logger.info(f"{'='*60}\n")

        # 1. READ context
        context = self._read_context()

        # 2. QUERY knowledge (simplified - no Qdrant)
        knowledge = self._query_knowledge(context)

        # 3. THINK
        decision = self._think(context, knowledge)

        # 4. ACT
        result = self._act(decision)

        # 5. RECORD
        self._record(decision, result)

        # 6. LEARN
        self._learn(decision, result)

    def _read_context(self):
        """Read recent context"""
        recent = self._recall_recent(10)

        context = {
            "recent_actions": [m for m in recent if m[2] == "action"],
            "recent_observations": [m for m in recent if m[2] == "observation"],
            "recent_preferences": [m for m in recent if m[2] == "preference"],
            "recent_goals": [m for m in recent if m[2] == "goal"]
        }

        logger.info("📖 READ Context:")
        logger.info(f"  Actions: {len(context['recent_actions'])}")
        logger.info(f"  Observations: {len(context['recent_observations'])}")
        logger.info(f"  Preferences: {len(context['recent_preferences'])}")

        # Show user preference if exists
        if context['recent_preferences']:
            pref = context['recent_preferences'][0][3]
            logger.info(f"  💡 User preference: {pref[:50]}...")

        return context

    def _query_knowledge(self, context):
        """Query knowledge (simplified)"""
        logger.info("🔍 QUERY Knowledge: (Qdrant disabled, using short-term only)")
        return []

    def _think(self, context, knowledge):
        """Decide what to do"""

        logger.info("💭 THINK:")

        # Check user preference for autonomous operation
        autonomous = any(
            'autonomous' in m[3].lower()
            for m in context['recent_preferences']
        )

        # Decision logic based on cycle
        if self.cycle_count % 5 == 0:
            decision = {
                "action": "self_check",
                "reasoning": "Regular self-assessment cycle",
                "priority": 6
            }
        elif autonomous:
            decision = {
                "action": "autonomous_learning",
                "reasoning": "User prefers autonomous operation - learning proactively",
                "priority": 7
            }
        else:
            decision = {
                "action": "monitor",
                "reasoning": "Standard monitoring",
                "priority": 5
            }

        logger.info(f"  Decision: {decision['action']}")
        logger.info(f"  Reasoning: {decision['reasoning']}")
        logger.info(f"  Priority: {decision['priority']}")

        return decision

    def _act(self, decision):
        """Execute decision"""

        logger.info(f"⚡ ACT: {decision['action']}")

        action = decision['action']

        try:
            if action == "autonomous_learning":
                # Simulate learning from environment
                result = {
                    "success": True,
                    "message": f"Analyzed patterns, found {self.cycle_count} cycles of data"
                }

            elif action == "self_check":
                # Health check
                recent = self._recall_recent(50)
                result = {
                    "success": True,
                    "message": f"Self-check OK: {len(recent)} memories, system healthy"
                }

            elif action == "monitor":
                # Standard monitoring
                result = {
                    "success": True,
                    "message": "Monitoring active, no anomalies detected"
                }

            else:
                result = {
                    "success": False,
                    "message": f"Unknown action: {action}"
                }

        except Exception as e:
            result = {
                "success": False,
                "message": f"Error: {e}"
            }

        logger.info(f"  Result: {result['message']}")
        return result

    def _record(self, decision, result):
        """Record to memory"""

        self._remember(
            "action",
            f"{decision['action']}: {result['message']}"
        )

        if result['success']:
            self._remember("observation", f"✅ {decision['action']} completed successfully")
        else:
            self._remember("observation", f"❌ {decision['action']} failed: {result['message']}")

        logger.info("📝 RECORD: Logged to short-term memory")

    def _learn(self, decision, result):
        """Learn from experience"""

        # Simplified learning (no Qdrant)
        if result['success'] and decision['priority'] >= 7:
            self._remember(
                "thought",
                f"Learned: {decision['action']} works well - use this approach"
            )
            logger.info("🧠 LEARN: Stored successful pattern")
        elif not result['success']:
            self._remember(
                "thought",
                f"Learned: {decision['action']} failed - avoid this"
            )
            logger.info("🧠 LEARN: Stored failure to avoid repeating")

    def _remember(self, type, content):
        """Store in short-term memory"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO memories (timestamp, type, content, metadata)
            VALUES (?, ?, ?, ?)
        """, (timestamp, type, content, None))

        conn.commit()

        # Keep only last 50
        cursor.execute("""
            DELETE FROM memories
            WHERE id NOT IN (
                SELECT id FROM memories
                ORDER BY timestamp DESC
                LIMIT 50
            )
        """)

        conn.commit()
        conn.close()

    def _recall_recent(self, limit=10):
        """Recall recent memories"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM memories
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return rows


def main():
    """Run autonomous worker"""

    print("🤖 PersonalAI Autonomous Worker (Standalone)\n")
    print("=" * 60)
    print()
    print("Decision Loop (every 5 seconds):")
    print("  1. READ   - Get context from memory")
    print("  2. QUERY  - Search knowledge (simplified)")
    print("  3. THINK  - Decide action")
    print("  4. ACT    - Execute")
    print("  5. RECORD - Log to memory")
    print("  6. LEARN  - Store insights")
    print()
    print("=" * 60)
    print()
    print("🚀 Starting autonomous operation...")
    print("⏸️  Press Ctrl+C to stop")
    print()

    worker = AutonomousWorkerStandalone()
    worker.start()


if __name__ == "__main__":
    main()
