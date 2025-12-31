"""
Enhanced Autonomous Worker with Vision + Reasoning

Uses AutonomousBrain for intelligent, vision-based autonomous operation.
This is the next evolution of autonomous_worker.py - with real intelligence.

Capabilities:
- Visual environment perception
- Reasoning-based decision making
- Goal-directed behavior
- Multi-modal sensing (dashcam, camera, internal state)
- Self-improving through experience
"""

import time
import logging
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.autonomous_brain import get_autonomous_brain
from core.autonomous_memory import remember_short, remember_long, recall_recent

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class EnhancedAutonomousWorker:
    """
    Enhanced autonomous worker with vision + reasoning

    Uses AutonomousBrain for intelligent decision-making
    """

    def __init__(self,
                 cycle_interval: int = 60,
                 enable_vision: bool = True):
        """
        Initialize enhanced autonomous worker

        Args:
            cycle_interval: Seconds between decision cycles
            enable_vision: Enable visual perception
        """
        self.brain = get_autonomous_brain()
        self.cycle_interval = cycle_interval
        self.enable_vision = enable_vision

        self.running = False
        self.cycle_count = 0

        # Capabilities (optional integrations)
        self.dashcam = None
        self.camera = None
        self.trader = None

        # Goals queue
        self.goals = []
        self.current_goal = None

        logger.info("🤖 Enhanced Autonomous Worker initialized")
        logger.info(f"   Vision enabled: {enable_vision}")
        logger.info(f"   Cycle interval: {cycle_interval}s")

    def set_goal(self, goal: str, priority: int = 5):
        """
        Set a goal for the autonomous worker

        Args:
            goal: Goal description
            priority: Priority 1-10 (higher = more urgent)
        """
        self.goals.append({
            "goal": goal,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        })

        # Sort by priority
        self.goals.sort(key=lambda x: x["priority"], reverse=True)

        logger.info(f"🎯 Goal set: {goal} (priority: {priority})")
        remember_short("goal", f"New goal: {goal} (priority: {priority})")

    def start(self):
        """Start enhanced autonomous operation"""
        self.running = True

        remember_short("action", "Enhanced autonomous worker started")
        logger.info("🚀 Enhanced Autonomous Worker starting...")
        logger.info("   Using vision + reasoning for intelligent decisions")

        # Optional: Initialize capabilities
        self._initialize_capabilities()

        # Main decision loop
        while self.running:
            try:
                # Get next goal if available
                if self.goals:
                    self.current_goal = self.goals[0]["goal"]
                else:
                    self.current_goal = "Maintain autonomous operation and learn"

                # Perception - get environment image if available
                environment_image = self._get_environment_image()

                # Run intelligent decision cycle with brain
                result = self.brain.autonomous_decision_cycle(
                    environment_image=environment_image,
                    user_goal=self.current_goal
                )

                self.cycle_count += 1

                # Log cycle result
                logger.info(f"\nCycle #{self.cycle_count} complete")
                logger.info(f"Decision: {result['decision']['action']}")
                logger.info(f"Success: {result['success']}")
                logger.info(f"Success rate: {self.brain.successful_decisions / max(1, self.brain.cycle_count):.1%}\n")

                # Check if goal completed
                if result['success'] and self.goals:
                    # Simple completion heuristic - successful high-confidence decision
                    if result['decision'].get('confidence', 0) >= 0.8:
                        completed_goal = self.goals.pop(0)
                        logger.info(f"✅ Goal completed: {completed_goal['goal']}")
                        remember_long(
                            type="achievement",
                            content=f"Completed goal: {completed_goal['goal']}",
                            tags=["goal", "completed", "success"],
                            importance=9
                        )

                # Sleep between cycles
                time.sleep(self.cycle_interval)

            except KeyboardInterrupt:
                logger.info("⏸️ Enhanced Autonomous Worker stopping...")
                self.running = False

            except Exception as e:
                logger.error(f"❌ Error in decision cycle: {e}")
                remember_short("observation", f"Cycle error: {e}")
                time.sleep(self.cycle_interval * 2)  # Wait longer after error

        remember_short("observation", "Enhanced autonomous operation stopped")
        logger.info("🛑 Enhanced Autonomous Worker stopped")

    def _initialize_capabilities(self):
        """Initialize optional capabilities (dashcam, camera, trader)"""

        # Try to initialize dashcam
        try:
            from modules.dashcam_ai import get_dashcam
            self.dashcam = get_dashcam()
            logger.info("   ✓ Dashcam capability enabled")
        except Exception as e:
            logger.info(f"   ⨯ Dashcam not available: {e}")

        # Try to initialize camera
        try:
            import cv2
            # Test camera
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                self.camera = cap
                logger.info("   ✓ Camera capability enabled")
            else:
                logger.info("   ⨯ Camera not available")
        except Exception as e:
            logger.info(f"   ⨯ Camera not available: {e}")

        # Try to initialize trader
        try:
            from trading.autonomous_trader import AutonomousTrader
            self.trader = AutonomousTrader(mode="paper")
            logger.info("   ✓ Trader capability enabled (paper mode)")
        except Exception as e:
            logger.info(f"   ⨯ Trader not available: {e}")

    def _get_environment_image(self) -> Optional[str]:
        """
        Get current environment image from available sources

        Priority:
        1. Dashcam (if monitoring)
        2. Camera (if available)
        3. None (internal perception only)

        Returns:
            Path to image or None
        """

        if not self.enable_vision:
            return None

        # Try dashcam first (most relevant for driving scenarios)
        if self.dashcam and self.dashcam.is_monitoring:
            try:
                # Get latest dashcam frame
                events = self.dashcam.get_events(limit=1)
                if events and events[0].snapshot_path:
                    image_path = events[0].snapshot_path
                    if Path(image_path).exists():
                        logger.info(f"   📷 Using dashcam image: {Path(image_path).name}")
                        return image_path
            except Exception as e:
                logger.debug(f"Could not get dashcam image: {e}")

        # Try camera
        if self.camera:
            try:
                import cv2
                ret, frame = self.camera.read()
                if ret:
                    # Save frame temporarily
                    image_path = config.CACHE_DIR / f"autonomous_perception_{self.cycle_count}.jpg"
                    cv2.imwrite(str(image_path), frame)
                    logger.info(f"   📷 Using camera image: {image_path.name}")
                    return str(image_path)
            except Exception as e:
                logger.debug(f"Could not get camera image: {e}")

        # No visual input available
        logger.info("   👁️ No visual input - using internal perception")
        return None

    def stop(self):
        """Stop autonomous operation"""
        logger.info("Stopping enhanced autonomous worker...")
        self.running = False

        # Cleanup
        if self.camera:
            try:
                self.camera.release()
            except:
                pass

    def get_status(self) -> Dict:
        """
        Get current status

        Returns:
            Status dict
        """
        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "brain_cycles": self.brain.cycle_count,
            "success_rate": self.brain.successful_decisions / max(1, self.brain.cycle_count),
            "current_goal": self.current_goal,
            "goals_queue": len(self.goals),
            "capabilities": {
                "vision": self.enable_vision,
                "dashcam": self.dashcam is not None,
                "camera": self.camera is not None,
                "trader": self.trader is not None
            }
        }


class MultiAgentCoordinator:
    """
    Coordinates multiple enhanced autonomous workers

    For complex scenarios requiring multiple specialized agents
    """

    def __init__(self):
        """Initialize multi-agent coordinator"""
        self.agents = {}
        self.running = False

        logger.info("🤝 Multi-Agent Coordinator initialized")

    def add_agent(self, name: str, agent: EnhancedAutonomousWorker):
        """
        Add agent to coordination

        Args:
            name: Agent name
            agent: Enhanced autonomous worker
        """
        self.agents[name] = agent
        logger.info(f"   Added agent: {name}")

    def start_all(self):
        """Start all agents in parallel"""
        import threading

        self.running = True

        threads = []
        for name, agent in self.agents.items():
            thread = threading.Thread(
                target=agent.start,
                name=f"Agent-{name}",
                daemon=True
            )
            thread.start()
            threads.append(thread)
            logger.info(f"   Started agent: {name}")

        logger.info(f"🚀 All {len(self.agents)} agents running")

        # Wait for all
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("⏸️ Stopping all agents...")
            self.stop_all()

    def stop_all(self):
        """Stop all agents"""
        for name, agent in self.agents.items():
            agent.stop()
            logger.info(f"   Stopped agent: {name}")

        self.running = False
        logger.info("🛑 All agents stopped")

    def get_status(self) -> Dict:
        """Get status of all agents"""
        return {
            "coordinator_running": self.running,
            "agent_count": len(self.agents),
            "agents": {
                name: agent.get_status()
                for name, agent in self.agents.items()
            }
        }


def main():
    """Run enhanced autonomous worker"""

    print("🤖 Enhanced Autonomous Worker with Vision + Reasoning\n")
    print("=" * 70)
    print()
    print("Decision Loop:")
    print("  1. PERCEIVE  - Use vision to understand environment")
    print("  2. RECALL    - Query memory for relevant knowledge")
    print("  3. REASON    - Use thinking mode to analyze situation")
    print("  4. DECIDE    - Choose optimal action based on reasoning")
    print("  5. ACT       - Execute decision")
    print("  6. REFLECT   - Learn from results")
    print()
    print("=" * 70)
    print()

    # Create worker
    worker = EnhancedAutonomousWorker(
        cycle_interval=60,  # 1 minute cycles
        enable_vision=True
    )

    # Set initial goals
    worker.set_goal("Monitor environment and detect important events", priority=8)
    worker.set_goal("Learn from patterns and improve decision-making", priority=7)
    worker.set_goal("Optimize autonomous operation performance", priority=6)

    print("Starting enhanced autonomous operation...")
    print("Press Ctrl+C to stop")
    print()

    # Start
    worker.start()


if __name__ == "__main__":
    main()
