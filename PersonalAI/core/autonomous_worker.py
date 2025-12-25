"""
PersonalAI Autonomous Worker Agent

Self-directed AI agent that:
- Monitors dashcam events
- Learns from patterns
- Makes autonomous decisions
- Improves over time

Decision Loop:
1. READ short-term memory (recent context)
2. QUERY long-term memory (relevant learnings)
3. THINK about what to do next
4. ACT - execute decision
5. RECORD - write to memory
6. LEARN - store significant discoveries
"""

import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.autonomous_memory import (
    get_short_term_memory,
    get_long_term_memory,
    remember_short,
    remember_long,
    recall_recent,
    recall_relevant
)

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class AutonomousWorker:
    """
    Autonomous PersonalAI Worker

    Runs continuously, making self-directed decisions
    """

    def __init__(self):
        self.short_memory = get_short_term_memory()
        self.long_memory = get_long_term_memory()

        self.running = False
        self.cycle_count = 0

        # Capabilities
        self.dashcam = None
        self.telegram_bot = None

        logger.info("🤖 Autonomous Worker initialized")

    def start(self):
        """Start autonomous operation"""
        self.running = True

        remember_short("goal", "Start autonomous operation")
        logger.info("🚀 Autonomous Worker starting...")

        # Main decision loop
        while self.running:
            try:
                self.decision_cycle()
                self.cycle_count += 1

                # Sleep between cycles
                time.sleep(30)  # 30 second cycles

            except KeyboardInterrupt:
                logger.info("⏸️ Autonomous Worker stopping...")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Error in decision cycle: {e}")
                remember_short("observation", f"Error: {e}")
                time.sleep(60)  # Wait longer after error

        remember_short("observation", "Autonomous operation stopped")
        logger.info("🛑 Autonomous Worker stopped")

    def decision_cycle(self):
        """
        Single decision cycle

        1. READ - Get context from short-term memory
        2. QUERY - Search long-term memory for relevant knowledge
        3. THINK - Analyze situation and decide action
        4. ACT - Execute decision
        5. RECORD - Log action and result
        6. LEARN - Store significant discoveries
        """

        logger.info(f"\n{'='*50}")
        logger.info(f"DECISION CYCLE #{self.cycle_count}")
        logger.info(f"{'='*50}\n")

        # 1. READ - Get recent context
        context = self._read_context()

        # 2. QUERY - Search for relevant past learnings
        relevant_knowledge = self._query_knowledge(context)

        # 3. THINK - Decide what to do
        decision = self._think(context, relevant_knowledge)

        # 4. ACT - Execute decision
        result = self._act(decision)

        # 5. RECORD - Log to short-term memory
        self._record(decision, result)

        # 6. LEARN - Store if significant
        self._learn(decision, result)

    def _read_context(self) -> Dict:
        """Read recent context from short-term memory"""
        recent_memories = recall_recent(limit=10)

        context = {
            "recent_actions": [],
            "recent_observations": [],
            "recent_goals": [],
            "recent_thoughts": []
        }

        for mem in recent_memories:
            if mem.type == "action":
                context["recent_actions"].append(mem.content)
            elif mem.type == "observation":
                context["recent_observations"].append(mem.content)
            elif mem.type == "goal":
                context["recent_goals"].append(mem.content)
            elif mem.type == "thought":
                context["recent_thoughts"].append(mem.content)

        logger.info("📖 READ Context:")
        logger.info(f"  Recent actions: {len(context['recent_actions'])}")
        logger.info(f"  Recent observations: {len(context['recent_observations'])}")
        logger.info(f"  Recent goals: {len(context['recent_goals'])}")

        return context

    def _query_knowledge(self, context: Dict) -> List:
        """Query long-term memory for relevant knowledge"""

        if not self.long_memory.enabled:
            return []

        # Build search query from context
        query_parts = []
        if context["recent_goals"]:
            query_parts.append(context["recent_goals"][-1])
        if context["recent_observations"]:
            query_parts.append(context["recent_observations"][-1])

        query = " ".join(query_parts) if query_parts else "autonomous operation"

        relevant = recall_relevant(query, limit=3)

        logger.info("🔍 QUERY Knowledge:")
        for mem in relevant:
            logger.info(f"  [{mem.type}] {mem.content[:60]}...")

        return relevant

    def _think(self, context: Dict, knowledge: List) -> Dict:
        """
        Analyze situation and decide what to do

        Returns decision dict with:
        - action: what to do
        - reasoning: why
        - priority: 1-10
        """

        logger.info("💭 THINK:")

        # Decision logic
        decision = None

        # Check if dashcam has events
        if self._should_check_dashcam_events():
            decision = {
                "action": "check_dashcam_events",
                "reasoning": "Regular dashcam event monitoring",
                "priority": 7
            }

        # Check if should analyze patterns
        elif self._should_analyze_patterns():
            decision = {
                "action": "analyze_patterns",
                "reasoning": "Time to analyze collected data for patterns",
                "priority": 6
            }

        # Check if should optimize
        elif self._should_optimize():
            decision = {
                "action": "optimize_performance",
                "reasoning": "Performance metrics suggest optimization needed",
                "priority": 5
            }

        # Default: self-improvement
        else:
            decision = {
                "action": "self_improvement",
                "reasoning": "No urgent tasks - focus on learning and improvement",
                "priority": 4
            }

        logger.info(f"  Decision: {decision['action']}")
        logger.info(f"  Reasoning: {decision['reasoning']}")
        logger.info(f"  Priority: {decision['priority']}")

        remember_short("thought", f"Decided to: {decision['action']} - {decision['reasoning']}")

        return decision

    def _act(self, decision: Dict) -> Dict:
        """Execute decision and return result"""

        logger.info(f"⚡ ACT: {decision['action']}")

        action = decision["action"]
        result = {"success": False, "message": ""}

        try:
            if action == "check_dashcam_events":
                result = self._check_dashcam_events()

            elif action == "analyze_patterns":
                result = self._analyze_patterns()

            elif action == "optimize_performance":
                result = self._optimize_performance()

            elif action == "self_improvement":
                result = self._self_improvement()

            else:
                result = {"success": False, "message": f"Unknown action: {action}"}

        except Exception as e:
            result = {"success": False, "message": f"Error: {e}"}
            logger.error(f"Action failed: {e}")

        logger.info(f"  Result: {result['message']}")
        return result

    def _record(self, decision: Dict, result: Dict):
        """Record action and result to short-term memory"""

        remember_short(
            "action",
            f"{decision['action']}: {result['message']}",
            metadata={"priority": decision["priority"], "success": result["success"]}
        )

        if result["success"]:
            remember_short("observation", f"Successfully completed: {decision['action']}")
        else:
            remember_short("observation", f"Failed: {decision['action']} - {result['message']}")

        logger.info("📝 RECORD: Action logged to memory")

    def _learn(self, decision: Dict, result: Dict):
        """Store significant discoveries in long-term memory"""

        if not self.long_memory.enabled:
            return

        # Only store successful high-priority actions
        if result["success"] and decision["priority"] >= 7:

            remember_long(
                type="lesson",
                content=f"{decision['action']} successful: {result['message']}",
                tags=["autonomous", decision["action"], "success"],
                importance=decision["priority"]
            )

            logger.info("🧠 LEARN: Stored lesson in long-term memory")

        # Store failures too (to avoid repeating)
        elif not result["success"] and decision["priority"] >= 6:

            remember_long(
                type="lesson",
                content=f"{decision['action']} failed: {result['message']} - avoid this approach",
                tags=["autonomous", decision["action"], "failure"],
                importance=decision["priority"]
            )

            logger.info("🧠 LEARN: Stored failure lesson to avoid repeating")

    # ===== DECISION LOGIC =====

    def _should_check_dashcam_events(self) -> bool:
        """Check if should monitor dashcam events"""
        # Every cycle check dashcam (if available)
        return True

    def _should_analyze_patterns(self) -> bool:
        """Check if should analyze patterns"""
        # Every 10 cycles
        return self.cycle_count % 10 == 0

    def _should_optimize(self) -> bool:
        """Check if should optimize performance"""
        # Every 20 cycles
        return self.cycle_count % 20 == 0

    # ===== ACTIONS =====

    def _check_dashcam_events(self) -> Dict:
        """Check dashcam for new events"""

        try:
            from modules.dashcam_ai import get_dashcam, EventType

            dashcam = get_dashcam()
            stats = dashcam.get_statistics()

            total_events = stats['total_events']
            critical_events = stats['events_by_severity'].get('critical', 0)

            # Get recent critical events
            critical = dashcam.get_events(severity="critical", limit=5)

            if critical:
                # New critical event detected!
                latest = critical[-1]

                message = f"Critical event detected: {latest.event_type.value} - {latest.description}"

                # Store in long-term memory
                remember_long(
                    type="discovery",
                    content=f"Dashcam critical event: {latest.event_type.value} at {latest.timestamp}",
                    tags=["dashcam", "critical", latest.event_type.value],
                    importance=9
                )

                # TODO: Send Telegram alert
                logger.warning(f"🚨 {message}")

                return {"success": True, "message": message}

            return {"success": True, "message": f"Dashcam monitored: {total_events} total events, {critical_events} critical"}

        except Exception as e:
            return {"success": False, "message": f"Dashcam check failed: {e}"}

    def _analyze_patterns(self) -> Dict:
        """Analyze data patterns and learn"""

        try:
            # Get all long-term memories
            discoveries = self.long_memory.get_all(type="discovery", limit=50)
            lessons = self.long_memory.get_all(type="lesson", limit=50)

            message = f"Analyzed {len(discoveries)} discoveries and {len(lessons)} lessons"

            # Look for patterns (simple frequency analysis)
            tags_frequency = {}
            for mem in discoveries + lessons:
                for tag in mem.tags:
                    tags_frequency[tag] = tags_frequency.get(tag, 0) + 1

            if tags_frequency:
                top_tag = max(tags_frequency, key=tags_frequency.get)
                message += f" - Most frequent topic: {top_tag} ({tags_frequency[top_tag]} occurrences)"

                # Store pattern discovery
                remember_long(
                    type="pattern",
                    content=f"Identified pattern: {top_tag} appears frequently in {tags_frequency[top_tag]} memories",
                    tags=["pattern", "analysis", top_tag],
                    importance=7
                )

            return {"success": True, "message": message}

        except Exception as e:
            return {"success": False, "message": f"Pattern analysis failed: {e}"}

    def _optimize_performance(self) -> Dict:
        """Optimize system performance"""

        try:
            # Analyze short-term memory size
            recent = recall_recent(50)

            action_count = sum(1 for m in recent if m.type == "action")
            observation_count = sum(1 for m in recent if m.type == "observation")

            message = f"Performance check: {action_count} actions, {observation_count} observations in recent memory"

            # Store optimization insight
            if action_count > observation_count * 2:
                remember_long(
                    type="lesson",
                    content="Too many actions without observations - need more monitoring",
                    tags=["optimization", "performance", "monitoring"],
                    importance=6
                )
                message += " - Recommendation: increase observation frequency"

            return {"success": True, "message": message}

        except Exception as e:
            return {"success": False, "message": f"Optimization failed: {e}"}

    def _self_improvement(self) -> Dict:
        """Self-improvement activities"""

        try:
            # Review recent failures
            recent = recall_recent(20)
            failures = [m for m in recent if m.metadata and not m.metadata.get("success", True)]

            if failures:
                latest_failure = failures[-1]
                message = f"Reviewing failure: {latest_failure.content}"

                # Learn from failure
                remember_long(
                    type="lesson",
                    content=f"Repeated failure pattern: {latest_failure.content} - needs different approach",
                    tags=["self-improvement", "failure-analysis"],
                    importance=7
                )

                return {"success": True, "message": message}

            # Otherwise, consolidate knowledge
            message = "Consolidating knowledge - no immediate improvements needed"

            return {"success": True, "message": message}

        except Exception as e:
            return {"success": False, "message": f"Self-improvement failed: {e}"}


def main():
    """Run autonomous worker"""

    print("🤖 PersonalAI Autonomous Worker\n")
    print("=" * 60)
    print()
    print("Decision Loop:")
    print("  1. READ   - Get context from short-term memory")
    print("  2. QUERY  - Search long-term memory for knowledge")
    print("  3. THINK  - Analyze and decide action")
    print("  4. ACT    - Execute decision")
    print("  5. RECORD - Log to memory")
    print("  6. LEARN  - Store significant discoveries")
    print()
    print("=" * 60)
    print()
    print("Starting autonomous operation...")
    print("Press Ctrl+C to stop")
    print()

    worker = AutonomousWorker()
    worker.start()


if __name__ == "__main__":
    main()
