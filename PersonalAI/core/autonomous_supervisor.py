"""
PersonalAI Autonomous Supervisor

Monitors worker agent via systemd timer
Ensures worker is healthy and performing well
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.autonomous_memory import (
    get_short_term_memory,
    get_long_term_memory,
    remember_short,
    remember_long,
    recall_recent
)

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class AutonomousSupervisor:
    """
    Supervisor agent

    Runs periodically (via systemd timer) to:
    - Check worker health
    - Analyze performance
    - Detect anomalies
    - Trigger interventions if needed
    """

    def __init__(self):
        self.short_memory = get_short_term_memory()
        self.long_memory = get_long_term_memory()

        logger.info("👁️ Supervisor initialized")

    def check(self):
        """
        Supervisor check cycle

        Called periodically by systemd timer
        """

        logger.info("\n" + "=" * 60)
        logger.info("SUPERVISOR CHECK")
        logger.info(f"Time: {datetime.now().isoformat()}")
        logger.info("=" * 60 + "\n")

        # Health checks
        worker_health = self._check_worker_health()
        memory_health = self._check_memory_health()
        performance = self._check_performance()

        # Generate report
        report = self._generate_report(worker_health, memory_health, performance)

        # Take action if needed
        if not worker_health["healthy"]:
            self._intervene("Worker unhealthy", worker_health)

        # Store supervisor check result
        remember_short("observation", f"Supervisor check complete - Worker: {worker_health['status']}")

        if self.long_memory.enabled:
            remember_long(
                type="fact",
                content=f"Supervisor check: Worker {worker_health['status']}, {memory_health['short_term_count']} recent memories",
                tags=["supervisor", "health-check"],
                importance=5
            )

        return report

    def _check_worker_health(self) -> Dict:
        """Check if worker is healthy"""

        # Check recent activity
        recent = recall_recent(limit=10)

        if not recent:
            return {
                "healthy": False,
                "status": "no_activity",
                "message": "No recent activity in short-term memory"
            }

        # Check last action timestamp
        latest = recent[0]
        latest_time = datetime.fromisoformat(latest.timestamp)
        time_since_last = datetime.now() - latest_time

        # Worker should act at least every 2 minutes
        if time_since_last > timedelta(minutes=2):
            return {
                "healthy": False,
                "status": "inactive",
                "message": f"No activity for {time_since_last.seconds}s - worker may be stuck"
            }

        # Check for error patterns
        errors = [m for m in recent if "error" in m.content.lower() or "failed" in m.content.lower()]

        if len(errors) > 5:
            return {
                "healthy": False,
                "status": "error_loop",
                "message": f"Too many errors: {len(errors)} errors in recent memory"
            }

        # All checks passed
        return {
            "healthy": True,
            "status": "healthy",
            "message": f"Worker active - last action {time_since_last.seconds}s ago"
        }

    def _check_memory_health(self) -> Dict:
        """Check memory system health"""

        recent = recall_recent(limit=50)

        result = {
            "short_term_count": len(recent),
            "long_term_enabled": self.long_memory.enabled
        }

        # Check if memory is filling up properly
        if len(recent) < 5:
            result["warning"] = "Low short-term memory usage - worker may not be recording properly"

        return result

    def _check_performance(self) -> Dict:
        """Check performance metrics"""

        recent = recall_recent(limit=20)

        actions = [m for m in recent if m.type == "action"]
        observations = [m for m in recent if m.type == "observation"]
        thoughts = [m for m in recent if m.type == "thought"]

        return {
            "actions": len(actions),
            "observations": len(observations),
            "thoughts": len(thoughts),
            "ratio": len(actions) / max(len(observations), 1)
        }

    def _generate_report(self, worker_health: Dict, memory_health: Dict, performance: Dict) -> str:
        """Generate human-readable report"""

        report = "📊 SUPERVISOR REPORT\n\n"

        # Worker health
        status_emoji = "✅" if worker_health["healthy"] else "❌"
        report += f"Worker Status: {status_emoji} {worker_health['status']}\n"
        report += f"  {worker_health['message']}\n\n"

        # Memory health
        report += f"Memory System:\n"
        report += f"  Short-term: {memory_health['short_term_count']} entries\n"
        report += f"  Long-term: {'✅ Enabled' if memory_health['long_term_enabled'] else '❌ Disabled'}\n"

        if memory_health.get("warning"):
            report += f"  ⚠️ {memory_health['warning']}\n"

        report += "\n"

        # Performance
        report += f"Performance:\n"
        report += f"  Actions: {performance['actions']}\n"
        report += f"  Observations: {performance['observations']}\n"
        report += f"  Thoughts: {performance['thoughts']}\n"
        report += f"  Action/Observation Ratio: {performance['ratio']:.2f}\n"

        logger.info(report)

        return report

    def _intervene(self, reason: str, context: Dict):
        """Take intervention action"""

        logger.warning(f"⚠️ INTERVENTION REQUIRED: {reason}")

        # Log intervention
        remember_short("observation", f"Supervisor intervention: {reason}")

        if self.long_memory.enabled:
            remember_long(
                type="lesson",
                content=f"Supervisor intervention needed: {reason} - {context}",
                tags=["supervisor", "intervention", "problem"],
                importance=8
            )

        # In production: restart worker, send alert, etc.
        # For now, just log

        logger.info(f"Context: {context}")


def main():
    """Run supervisor check (called by systemd timer)"""

    print("👁️ PersonalAI Autonomous Supervisor\n")

    supervisor = AutonomousSupervisor()
    report = supervisor.check()

    print("\n" + report)
    print("\n✅ Supervisor check complete")


if __name__ == "__main__":
    main()
