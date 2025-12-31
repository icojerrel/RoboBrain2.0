"""
PersonalAI Autonomous Brain - Core Intelligence

Integrates RoboBrain's vision + reasoning with autonomous decision-making.
This is the "thinking" core that powers autonomous behavior.

Decision Loop with Vision:
1. PERCEIVE - Use vision to understand environment
2. RECALL - Query memory for relevant knowledge
3. REASON - Use thinking mode to analyze and plan
4. DECIDE - Choose optimal action
5. ACT - Execute decision
6. REFLECT - Learn from results
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.brain import get_brain
from core.autonomous_memory import (
    remember_short,
    remember_long,
    recall_recent,
    recall_relevant
)

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class AutonomousBrain:
    """
    The autonomous intelligence core

    Combines RoboBrain's vision + reasoning with memory-based learning
    to create truly autonomous decision-making.
    """

    def __init__(self):
        """Initialize autonomous brain with vision capabilities"""
        self.brain = get_brain()
        self.cycle_count = 0

        # State
        self.current_goal = None
        self.current_context = {}
        self.last_perception = None

        # Performance tracking
        self.successful_decisions = 0
        self.failed_decisions = 0

        logger.info("🧠 Autonomous Brain initialized with vision+reasoning")

    def autonomous_decision_cycle(self,
                                  environment_image: Optional[str] = None,
                                  user_goal: Optional[str] = None) -> Dict:
        """
        Single autonomous decision cycle with vision+reasoning

        Args:
            environment_image: Optional image for visual perception
            user_goal: Optional explicit goal from user

        Returns:
            Dict with decision, reasoning, and result
        """

        self.cycle_count += 1

        logger.info(f"\n{'='*60}")
        logger.info(f"AUTONOMOUS BRAIN CYCLE #{self.cycle_count}")
        logger.info(f"{'='*60}\n")

        # Update goal if provided
        if user_goal:
            self.current_goal = user_goal
            remember_short("goal", user_goal)

        # 1. PERCEIVE - Understand environment through vision
        perception = self._perceive(environment_image)

        # 2. RECALL - Get relevant knowledge from memory
        knowledge = self._recall(perception)

        # 3. REASON - Use thinking mode to analyze situation
        analysis = self._reason(perception, knowledge)

        # 4. DECIDE - Choose optimal action based on reasoning
        decision = self._decide(analysis)

        # 5. ACT - Execute decision (returns simulated result)
        result = self._act(decision)

        # 6. REFLECT - Learn from results
        self._reflect(decision, result)

        return {
            "cycle": self.cycle_count,
            "perception": perception,
            "analysis": analysis,
            "decision": decision,
            "result": result,
            "success": result["success"]
        }

    def _perceive(self, image_path: Optional[str] = None) -> Dict:
        """
        PERCEIVE step - Use vision to understand environment

        Args:
            image_path: Path to image (optional)

        Returns:
            Dict with perception results
        """

        logger.info("👁️ PERCEIVE: Understanding environment...")

        if not image_path:
            # No image - perceive internal state
            perception = {
                "type": "internal",
                "state": "operational",
                "description": "No visual input - relying on memory and internal state"
            }

            logger.info("  Internal perception: operational state")
            return perception

        try:
            # Use RoboBrain vision to analyze environment
            prompt = """Analyze this environment comprehensively:
1. What objects and entities are present?
2. What activities or events are happening?
3. What opportunities for action exist?
4. What potential issues or risks do you observe?

Provide a detailed autonomous perception."""

            result = self.brain.deep_analyze(image_path, prompt)

            perception = {
                "type": "visual",
                "image": image_path,
                "description": result["answer"],
                "reasoning": result.get("thinking", ""),
                "timestamp": datetime.now().isoformat()
            }

            # Store perception
            remember_short("observation", f"Visual perception: {result['answer'][:100]}...")

            logger.info(f"  Visual perception: {result['answer'][:80]}...")

            self.last_perception = perception
            return perception

        except Exception as e:
            logger.error(f"  Perception failed: {e}")
            return {
                "type": "error",
                "description": f"Visual perception failed: {e}",
                "timestamp": datetime.now().isoformat()
            }

    def _recall(self, perception: Dict) -> List[Dict]:
        """
        RECALL step - Query memory for relevant knowledge

        Args:
            perception: Current perception

        Returns:
            List of relevant memories
        """

        logger.info("📚 RECALL: Querying memory for relevant knowledge...")

        # Build search query from perception
        query = perception.get("description", "autonomous operation")

        # Get relevant long-term memories
        relevant = recall_relevant(query, limit=5)

        # Get recent context
        recent = recall_recent(limit=10)

        knowledge = {
            "relevant_lessons": [m for m in relevant if m.type in ["lesson", "discovery"]],
            "relevant_patterns": [m for m in relevant if m.type == "pattern"],
            "recent_context": recent
        }

        logger.info(f"  Relevant lessons: {len(knowledge['relevant_lessons'])}")
        logger.info(f"  Relevant patterns: {len(knowledge['relevant_patterns'])}")
        logger.info(f"  Recent context: {len(knowledge['recent_context'])}")

        return knowledge

    def _reason(self, perception: Dict, knowledge: Dict) -> Dict:
        """
        REASON step - Use thinking mode to analyze situation

        Args:
            perception: Current perception
            knowledge: Recalled knowledge

        Returns:
            Analysis with reasoning
        """

        logger.info("💭 REASON: Analyzing situation with thinking mode...")

        # Build reasoning prompt
        context_parts = []

        # Add perception
        context_parts.append(f"Current Perception: {perception.get('description', 'None')}")

        # Add goal
        if self.current_goal:
            context_parts.append(f"Current Goal: {self.current_goal}")

        # Add relevant lessons
        if knowledge["relevant_lessons"]:
            lessons_text = "\n".join([f"- {m.content}" for m in knowledge["relevant_lessons"][:3]])
            context_parts.append(f"Relevant Lessons:\n{lessons_text}")

        # Add patterns
        if knowledge["relevant_patterns"]:
            pattern = knowledge["relevant_patterns"][0]
            context_parts.append(f"Known Pattern: {pattern.content}")

        # Construct reasoning prompt
        reasoning_prompt = f"""You are an autonomous AI analyzing a situation.

{chr(10).join(context_parts)}

Based on this context, reason about:
1. What is the current state of the situation?
2. What are the most important factors to consider?
3. What are the possible actions you could take?
4. What are the potential outcomes of each action?
5. What is the optimal decision and why?

Provide deep analytical reasoning."""

        # Use brain's thinking mode (if available)
        if not perception.get("image"):
            # No image - use text-based reasoning
            analysis = {
                "reasoning": self._text_based_reasoning(context_parts),
                "confidence": 0.7,
                "factors": ["memory", "context", "goals"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Vision-based reasoning
            try:
                result = self.brain.deep_analyze(
                    perception["image"],
                    reasoning_prompt
                )

                analysis = {
                    "reasoning": result.get("thinking", result.get("answer", "")),
                    "conclusion": result.get("answer", ""),
                    "confidence": 0.9,
                    "factors": ["vision", "memory", "reasoning"],
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"  Vision-based reasoning failed: {e}")
                analysis = {
                    "reasoning": self._text_based_reasoning(context_parts),
                    "confidence": 0.5,
                    "factors": ["context"],
                    "error": str(e)
                }

        logger.info(f"  Analysis confidence: {analysis['confidence']}")
        logger.info(f"  Factors considered: {', '.join(analysis['factors'])}")

        # Store reasoning
        remember_short("thought", f"Reasoning: {analysis.get('reasoning', 'N/A')[:100]}...")

        return analysis

    def _text_based_reasoning(self, context_parts: List[str]) -> str:
        """Fallback text-based reasoning when vision unavailable"""

        context_summary = " | ".join(context_parts)

        # Simple rule-based reasoning
        reasoning = f"""Analyzing current context: {context_summary}

Situation Assessment:
- Autonomous operation mode: Active
- Goal status: {'Defined' if self.current_goal else 'Undefined'}
- Cycle: #{self.cycle_count}
- Performance: {self.successful_decisions} successes, {self.failed_decisions} failures

Reasoning:
Since we have {len(context_parts)} context factors to consider, we should:
1. Prioritize current goal if defined
2. Use past lessons to inform decision
3. Maintain stable autonomous operation
4. Learn from each cycle

Optimal approach: Continue autonomous operation with careful monitoring."""

        return reasoning

    def _decide(self, analysis: Dict) -> Dict:
        """
        DECIDE step - Choose optimal action based on reasoning

        Args:
            analysis: Reasoning analysis

        Returns:
            Decision dict
        """

        logger.info("🎯 DECIDE: Choosing optimal action...")

        # Extract decision from reasoning
        reasoning = analysis.get("reasoning", "")
        conclusion = analysis.get("conclusion", "")

        # Decision logic based on confidence and context
        if analysis.get("confidence", 0) >= 0.8:
            # High confidence - autonomous decision
            decision = {
                "action": "autonomous_operation",
                "type": "autonomous",
                "reasoning": reasoning,
                "confidence": analysis["confidence"],
                "parameters": {
                    "mode": "proactive",
                    "monitoring": "continuous"
                }
            }

        elif analysis.get("confidence", 0) >= 0.5:
            # Medium confidence - cautious approach
            decision = {
                "action": "monitored_operation",
                "type": "cautious",
                "reasoning": reasoning,
                "confidence": analysis["confidence"],
                "parameters": {
                    "mode": "reactive",
                    "monitoring": "increased"
                }
            }

        else:
            # Low confidence - conservative approach
            decision = {
                "action": "observe_and_learn",
                "type": "conservative",
                "reasoning": reasoning,
                "confidence": analysis["confidence"],
                "parameters": {
                    "mode": "observation",
                    "monitoring": "maximum"
                }
            }

        logger.info(f"  Decision: {decision['action']}")
        logger.info(f"  Type: {decision['type']}")
        logger.info(f"  Confidence: {decision['confidence']}")

        # Store decision
        remember_short("thought", f"Decision: {decision['action']} (confidence: {decision['confidence']})")

        return decision

    def _act(self, decision: Dict) -> Dict:
        """
        ACT step - Execute decision

        Args:
            decision: Decision to execute

        Returns:
            Result dict
        """

        logger.info(f"⚡ ACT: Executing {decision['action']}...")

        action = decision["action"]

        # Execute action (currently simulated)
        try:
            if action == "autonomous_operation":
                result = {
                    "success": True,
                    "message": "Autonomous operation proceeding successfully",
                    "outcome": "continued_operation",
                    "metrics": {
                        "confidence": decision["confidence"],
                        "mode": decision["parameters"]["mode"]
                    }
                }

            elif action == "monitored_operation":
                result = {
                    "success": True,
                    "message": "Operating with increased monitoring",
                    "outcome": "cautious_continuation",
                    "metrics": {
                        "confidence": decision["confidence"],
                        "monitoring_level": "increased"
                    }
                }

            elif action == "observe_and_learn":
                result = {
                    "success": True,
                    "message": "Observation mode - gathering data for learning",
                    "outcome": "learning_phase",
                    "metrics": {
                        "data_collected": True,
                        "learning_mode": True
                    }
                }

            else:
                result = {
                    "success": False,
                    "message": f"Unknown action: {action}",
                    "outcome": "error"
                }

            logger.info(f"  Result: {result['message']}")

            # Store action result
            remember_short(
                "action",
                f"{action}: {result['message']}",
                metadata={"success": result["success"], "outcome": result["outcome"]}
            )

            return result

        except Exception as e:
            logger.error(f"  Action execution failed: {e}")
            result = {
                "success": False,
                "message": f"Execution failed: {e}",
                "outcome": "error",
                "error": str(e)
            }

            remember_short("observation", f"Action failed: {e}")
            return result

    def _reflect(self, decision: Dict, result: Dict):
        """
        REFLECT step - Learn from results

        Args:
            decision: Decision that was made
            result: Result of execution
        """

        logger.info("🔄 REFLECT: Learning from results...")

        # Update performance metrics
        if result["success"]:
            self.successful_decisions += 1
        else:
            self.failed_decisions += 1

        success_rate = self.successful_decisions / max(1, self.cycle_count)

        logger.info(f"  Success rate: {success_rate:.1%}")
        logger.info(f"  Total cycles: {self.cycle_count}")

        # Store significant learnings in long-term memory
        if result["success"] and decision["confidence"] >= 0.8:
            # High-confidence success - store as best practice
            remember_long(
                type="lesson",
                content=f"Successful {decision['action']} with {decision['confidence']:.1%} confidence: {result['message']}",
                tags=["success", decision["action"], "high-confidence"],
                importance=8
            )
            logger.info("  ✓ Stored success lesson in long-term memory")

        elif not result["success"]:
            # Failure - store to avoid repeating
            remember_long(
                type="lesson",
                content=f"Failed {decision['action']}: {result['message']} - requires different approach",
                tags=["failure", decision["action"], "avoid"],
                importance=7
            )
            logger.info("  ✗ Stored failure lesson to avoid repeating")

        # Detect patterns
        if self.cycle_count % 10 == 0:
            # Every 10 cycles, analyze patterns
            pattern_insight = f"After {self.cycle_count} cycles: {success_rate:.1%} success rate"

            if success_rate > 0.8:
                pattern_insight += " - Excellent autonomous performance"
                importance = 9
            elif success_rate > 0.6:
                pattern_insight += " - Good autonomous performance"
                importance = 7
            else:
                pattern_insight += " - Need improvement in decision-making"
                importance = 8

            remember_long(
                type="pattern",
                content=pattern_insight,
                tags=["performance", "autonomous", "pattern"],
                importance=importance
            )

            logger.info(f"  📊 Pattern identified: {pattern_insight}")

        # Store reflection
        remember_short(
            "thought",
            f"Reflection: {success_rate:.1%} success rate after {self.cycle_count} cycles"
        )


# Singleton instance
_autonomous_brain_instance: Optional[AutonomousBrain] = None

def get_autonomous_brain() -> AutonomousBrain:
    """Get or create autonomous brain singleton"""
    global _autonomous_brain_instance
    if _autonomous_brain_instance is None:
        _autonomous_brain_instance = AutonomousBrain()
    return _autonomous_brain_instance


# Test
if __name__ == "__main__":
    print("🧠 Autonomous Brain Test\n")
    print("=" * 60)

    brain = get_autonomous_brain()

    # Test cycle without image
    print("\n1. Testing internal perception cycle...")
    result = brain.autonomous_decision_cycle()
    print(f"   Result: {result['result']['message']}")
    print(f"   Success: {result['success']}")

    # Test cycle with goal
    print("\n2. Testing goal-directed cycle...")
    result = brain.autonomous_decision_cycle(user_goal="Optimize system performance")
    print(f"   Result: {result['result']['message']}")
    print(f"   Success: {result['success']}")

    print("\n" + "=" * 60)
    print("✅ Autonomous Brain ready for operation!")
