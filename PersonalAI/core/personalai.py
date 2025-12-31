"""
PersonalAI Core - Unified Intelligence System

Integrates all PersonalAI components into one coherent system:
- RoboBrain vision + reasoning (brain.py)
- Autonomous intelligence (autonomous_brain.py)
- Enhanced autonomous worker (enhanced_autonomous_worker.py)
- Memory systems (autonomous_memory.py)
- Trading (autonomous_trader.py)
- Dashcam AI (dashcam_ai.py)

This is the main entry point for PersonalAI capabilities.
"""

import logging
from typing import Optional, Dict, List, Union
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
import config

# Core components
from core.brain import get_brain, PersonalBrain
from core.autonomous_brain import get_autonomous_brain, AutonomousBrain
from core.enhanced_autonomous_worker import (
    EnhancedAutonomousWorker,
    MultiAgentCoordinator
)
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


class PersonalAI:
    """
    Unified PersonalAI system

    Combines all capabilities into one intelligent assistant:
    - Vision and spatial reasoning
    - Autonomous decision-making
    - Memory and learning
    - Multi-modal perception
    - Goal-directed behavior
    """

    def __init__(self,
                 enable_autonomous: bool = True,
                 enable_vision: bool = True,
                 enable_memory: bool = True):
        """
        Initialize PersonalAI system

        Args:
            enable_autonomous: Enable autonomous mode
            enable_vision: Enable vision capabilities
            enable_memory: Enable long-term memory
        """

        logger.info("🚀 Initializing PersonalAI Core System...")

        # Core components
        self.brain = get_brain()
        self.autonomous_brain = get_autonomous_brain() if enable_autonomous else None
        self.worker = None

        # Configuration
        self.enable_autonomous = enable_autonomous
        self.enable_vision = enable_vision
        self.enable_memory = enable_memory

        # State
        self.mode = "manual"  # manual, autonomous, or hybrid
        self.current_task = None

        logger.info("✅ PersonalAI Core initialized")
        logger.info(f"   Autonomous: {enable_autonomous}")
        logger.info(f"   Vision: {enable_vision}")
        logger.info(f"   Memory: {enable_memory}")

    # ===== Vision Capabilities =====

    def analyze_image(self,
                     image: Union[str, List[str]],
                     question: str,
                     thinking: bool = True) -> Dict:
        """
        Analyze image(s) with RoboBrain

        Args:
            image: Image path or list of paths
            question: Question about image
            thinking: Enable thinking mode

        Returns:
            Analysis result
        """
        logger.info(f"🔍 Analyzing image: {question}")

        result = self.brain.analyze(
            image=image,
            prompt=question,
            task="general",
            thinking=thinking
        )

        # Store in memory
        if self.enable_memory:
            remember_short("observation", f"Vision analysis: {result['answer'][:100]}...")

        return result

    def find_object(self,
                   image: str,
                   object_description: str,
                   visualize: bool = True) -> Dict:
        """
        Find object in image with bounding boxes

        Args:
            image: Image path
            object_description: Object to find
            visualize: Save visualization

        Returns:
            Detection result with coordinates
        """
        logger.info(f"🎯 Finding: {object_description}")

        result = self.brain.find_objects(
            image=image,
            object_description=object_description,
            plot=visualize
        )

        if self.enable_memory:
            remember_short("action", f"Object detection: {object_description}")

        return result

    def get_robot_action(self,
                        image: str,
                        action: str,
                        task_type: str = "affordance") -> Dict:
        """
        Get robot action plan for manipulation

        Args:
            image: Scene image
            action: Desired action (e.g., "pick up the cup")
            task_type: affordance, trajectory, or pointing

        Returns:
            Action plan with coordinates
        """
        logger.info(f"🤖 Planning robot action: {action}")

        result = self.brain.analyze(
            image=image,
            prompt=action,
            task=task_type,
            thinking=True,
            plot=True
        )

        if self.enable_memory:
            remember_short("action", f"Robot planning: {action}")

        return result

    # ===== Autonomous Capabilities =====

    def start_autonomous_mode(self,
                             goals: Optional[List[str]] = None,
                             cycle_interval: int = 60):
        """
        Start autonomous operation

        Args:
            goals: Initial goals list
            cycle_interval: Seconds between decision cycles
        """

        if not self.enable_autonomous:
            logger.error("Autonomous mode not enabled")
            return

        logger.info("🤖 Starting autonomous mode...")

        # Create enhanced worker
        self.worker = EnhancedAutonomousWorker(
            cycle_interval=cycle_interval,
            enable_vision=self.enable_vision
        )

        # Set goals
        if goals:
            for i, goal in enumerate(goals):
                priority = 10 - i  # Descending priority
                self.worker.set_goal(goal, priority=priority)

        self.mode = "autonomous"

        # Start worker in background thread
        import threading
        worker_thread = threading.Thread(
            target=self.worker.start,
            daemon=True
        )
        worker_thread.start()

        logger.info("✅ Autonomous mode started")

    def stop_autonomous_mode(self):
        """Stop autonomous operation"""

        if self.worker:
            self.worker.stop()
            self.mode = "manual"
            logger.info("🛑 Autonomous mode stopped")

    def set_goal(self, goal: str, priority: int = 5):
        """
        Set goal for autonomous mode

        Args:
            goal: Goal description
            priority: Priority 1-10
        """

        if self.mode == "autonomous" and self.worker:
            self.worker.set_goal(goal, priority)
        else:
            logger.warning("Not in autonomous mode - goal queued for next autonomous session")
            remember_short("goal", f"Queued goal: {goal} (priority: {priority})")

    # ===== Memory Capabilities =====

    def remember(self,
                content: str,
                type: str = "observation",
                importance: int = 5,
                tags: Optional[List[str]] = None):
        """
        Store memory

        Args:
            content: Memory content
            type: Memory type (observation, action, thought, goal, lesson, etc.)
            importance: Importance 1-10 (>=5 goes to long-term)
            tags: Optional tags for categorization
        """

        # Short-term memory
        remember_short(type, content)

        # Long-term memory if important
        if importance >= 5 and self.enable_memory:
            remember_long(
                type=type,
                content=content,
                tags=tags or [type],
                importance=importance
            )

        logger.info(f"💾 Stored memory: {content[:50]}...")

    def recall(self,
              query: str,
              limit: int = 5) -> List:
        """
        Recall relevant memories

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of relevant memories
        """

        if not self.enable_memory:
            logger.warning("Long-term memory not enabled")
            return []

        memories = recall_relevant(query, limit=limit)

        logger.info(f"🔍 Recalled {len(memories)} memories for: {query}")

        return memories

    def get_recent_context(self, limit: int = 10) -> List:
        """
        Get recent context from short-term memory

        Args:
            limit: Number of recent memories

        Returns:
            Recent memories
        """

        recent = recall_recent(limit=limit)
        logger.info(f"📖 Retrieved {len(recent)} recent memories")

        return recent

    # ===== Intelligence & Reasoning =====

    def think_about(self,
                   situation: str,
                   context_image: Optional[str] = None) -> Dict:
        """
        Deep reasoning about a situation

        Args:
            situation: Situation description or question
            context_image: Optional image for visual context

        Returns:
            Reasoning result
        """

        logger.info(f"💭 Thinking about: {situation}")

        if context_image:
            # Vision-based reasoning
            result = self.brain.deep_analyze(
                image=context_image,
                prompt=f"Think deeply about this situation: {situation}\n\nProvide detailed reasoning and analysis."
            )
        else:
            # Text-based reasoning (would need LLM integration for full capability)
            result = {
                "thinking": f"Analyzing situation: {situation}\n\nBased on available context and memory, this requires careful consideration.",
                "answer": "For full reasoning without images, integration with LLM (GPT/Claude) needed."
            }

        if self.enable_memory:
            remember_short("thought", f"Reasoning: {result.get('thinking', '')[:100]}...")

        return result

    def make_decision(self,
                     options: List[str],
                     criteria: str,
                     context_image: Optional[str] = None) -> Dict:
        """
        Make intelligent decision between options

        Args:
            options: List of possible options
            criteria: Decision criteria
            context_image: Optional visual context

        Returns:
            Decision with reasoning
        """

        logger.info(f"🎯 Making decision: {criteria}")
        logger.info(f"   Options: {', '.join(options)}")

        # Use autonomous brain for decision-making
        if self.autonomous_brain and context_image:
            # Run decision cycle
            result = self.autonomous_brain.autonomous_decision_cycle(
                environment_image=context_image,
                user_goal=f"Decide between {', '.join(options)} based on: {criteria}"
            )

            decision = {
                "chosen_option": result["decision"]["action"],
                "reasoning": result["decision"]["reasoning"],
                "confidence": result["decision"]["confidence"],
                "success": result["success"]
            }

        else:
            # Fallback decision logic
            decision = {
                "chosen_option": options[0] if options else "No option",
                "reasoning": f"Selected based on: {criteria}",
                "confidence": 0.5,
                "success": True
            }

        if self.enable_memory:
            remember_short(
                "thought",
                f"Decision: {decision['chosen_option']} - {decision['reasoning'][:80]}"
            )

        return decision

    # ===== System Management =====

    def get_status(self) -> Dict:
        """
        Get system status

        Returns:
            Status dict
        """

        status = {
            "mode": self.mode,
            "components": {
                "brain": self.brain.is_ready,
                "autonomous_brain": self.autonomous_brain is not None,
                "worker": self.worker is not None and self.worker.running if self.worker else False
            },
            "capabilities": {
                "vision": self.enable_vision,
                "autonomous": self.enable_autonomous,
                "memory": self.enable_memory
            },
            "current_task": self.current_task
        }

        # Add worker status if available
        if self.worker:
            status["worker_status"] = self.worker.get_status()

        # Add brain stats
        if self.autonomous_brain:
            status["brain_stats"] = {
                "cycles": self.autonomous_brain.cycle_count,
                "success_rate": self.autonomous_brain.successful_decisions / max(1, self.autonomous_brain.cycle_count),
                "total_successes": self.autonomous_brain.successful_decisions,
                "total_failures": self.autonomous_brain.failed_decisions
            }

        return status

    def get_capabilities(self) -> Dict:
        """Get system capabilities"""

        return {
            "vision_tasks": ["general", "pointing", "affordance", "trajectory", "grounding"],
            "autonomous_modes": ["manual", "autonomous", "hybrid"],
            "memory_types": ["short_term", "long_term"],
            "thinking_support": self.brain.model.supports_thinking,
            "model": self.brain.model_id,
            "status": "ready" if self.brain.is_ready else "not_ready"
        }


# Singleton instance
_personalai_instance: Optional[PersonalAI] = None

def get_personalai(
    enable_autonomous: bool = True,
    enable_vision: bool = True,
    enable_memory: bool = True
) -> PersonalAI:
    """
    Get or create PersonalAI singleton

    Args:
        enable_autonomous: Enable autonomous capabilities
        enable_vision: Enable vision capabilities
        enable_memory: Enable long-term memory

    Returns:
        PersonalAI instance
    """
    global _personalai_instance

    if _personalai_instance is None:
        _personalai_instance = PersonalAI(
            enable_autonomous=enable_autonomous,
            enable_vision=enable_vision,
            enable_memory=enable_memory
        )

    return _personalai_instance


# Test
if __name__ == "__main__":
    print("🤖 PersonalAI Core System\n")
    print("=" * 70)
    print()

    # Initialize
    ai = get_personalai(
        enable_autonomous=True,
        enable_vision=True,
        enable_memory=True
    )

    print("Capabilities:")
    caps = ai.get_capabilities()
    for key, value in caps.items():
        print(f"  {key}: {value}")

    print("\nStatus:")
    status = ai.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("✅ PersonalAI Core ready!")
