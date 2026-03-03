"""
PersonalAI Test Suite - Core Components

Tests for brain, memory, and autonomous components
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestBrain:
    """Tests for core/brain.py"""

    @pytest.fixture
    def brain(self):
        """Create brain instance for testing"""
        with patch('core.brain.UnifiedInference'):
            from core.brain import PersonalBrain
            return PersonalBrain(model_id="BAAI/RoboBrain2.0-7B")

    def test_brain_initialization(self, brain):
        """Test brain initializes correctly"""
        assert brain.model_id == "BAAI/RoboBrain2.0-7B"
        assert brain.is_ready

    def test_analyze_image(self, brain):
        """Test image analysis"""
        # Mock the model inference
        brain.model.inference = Mock(return_value={
            'answer': 'Test answer',
            'thinking': 'Test reasoning'
        })

        result = brain.analyze("test.jpg", "What is this?")

        assert 'answer' in result
        assert result['answer'] == 'Test answer'
        assert result['task_type'] == 'general'

    def test_quick_analyze(self, brain):
        """Test quick analysis without thinking"""
        brain.model.inference = Mock(return_value={
            'answer': 'Quick answer'
        })

        result = brain.quick_analyze("test.jpg", "Quick question?")

        assert result == 'Quick answer'
        # Verify thinking was disabled
        brain.model.inference.assert_called_with(
            text="Quick question?",
            image="test.jpg",
            task='general',
            enable_thinking=False,
            plot=False,
            do_sample=True,
            temperature=0.7
        )

    def test_find_objects(self, brain):
        """Test object detection"""
        brain.model.inference = Mock(return_value={
            'answer': 'Found objects',
            'boxes': [[10, 10, 50, 50]]
        })

        result = brain.find_objects("test.jpg", "red cup")

        brain.model.inference.assert_called_with(
            text="red cup",
            image="test.jpg",
            task='grounding',
            enable_thinking=True,
            plot=True,
            do_sample=True,
            temperature=0.7
        )

    def test_get_capabilities(self, brain):
        """Test capabilities report"""
        brain.model.supports_thinking = True

        caps = brain.get_capabilities()

        assert caps['model'] == "BAAI/RoboBrain2.0-7B"
        assert caps['thinking_support'] == True
        assert caps['ready'] == True
        assert 'general' in caps['tasks']


class TestMemory:
    """Tests for autonomous memory system"""

    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create temporary database for testing"""
        db_path = tmp_path / "test_memory.db"
        return str(db_path)

    def test_short_term_memory(self, temp_db):
        """Test short-term memory storage and recall"""
        from core.autonomous_memory import ShortTermMemoryStore

        store = ShortTermMemoryStore(db_path=temp_db)

        # Add memories
        store.add("observation", "Test observation 1")
        store.add("action", "Test action 1")
        store.add("thought", "Test thought 1")

        # Recall recent
        memories = store.get_recent(limit=10)

        assert len(memories) == 3
        assert memories[0].type == "observation"
        assert memories[0].content == "Test observation 1"

    def test_short_term_memory_limit(self, temp_db):
        """Test short-term memory keeps only last 50"""
        from core.autonomous_memory import ShortTermMemoryStore

        store = ShortTermMemoryStore(db_path=temp_db)

        # Add 60 memories
        for i in range(60):
            store.add("observation", f"Test {i}")

        # Should only have 50
        memories = store.get_recent(limit=100)
        assert len(memories) == 50

        # Should have newest ones (50-59)
        assert "Test 59" in memories[-1].content

    def test_memory_by_type(self, temp_db):
        """Test filtering memories by type"""
        from core.autonomous_memory import ShortTermMemoryStore

        store = ShortTermMemoryStore(db_path=temp_db)

        store.add("observation", "Observation 1")
        store.add("action", "Action 1")
        store.add("observation", "Observation 2")

        observations = store.get_by_type("observation", limit=10)
        actions = store.get_by_type("action", limit=10)

        assert len(observations) == 2
        assert len(actions) == 1


class TestRiskManager:
    """Tests for trading risk manager"""

    @pytest.fixture
    def risk_manager(self):
        """Create risk manager for testing"""
        from trading.risk_manager import RiskManager
        return RiskManager()

    def test_position_size_calculation(self, risk_manager):
        """Test position size calculation"""
        size = risk_manager.calculate_position_size(
            account_balance=100000,
            risk_percent=1.0,
            stop_loss_points=50
        )

        # $100k account, 1% risk = $1000 risk
        # $1000 / 50 points = 20 contracts
        assert size == 20

    def test_daily_risk_limit(self, risk_manager):
        """Test daily risk limit enforcement"""
        # Simulate losing 3% today
        risk_manager.daily_loss = 3000  # $3k on $100k account

        risk_assessment = risk_manager.assess_trade(
            symbol="MNQ",
            direction="LONG",
            entry_price=18500,
            account_balance=100000,
            atr=85
        )

        # Should reject - daily limit reached
        assert risk_assessment.approved == False
        assert "Daily loss limit" in risk_assessment.reason

    def test_max_positions_limit(self, risk_manager):
        """Test max concurrent positions limit"""
        # Add 3 existing positions
        risk_manager.open_positions = [
            {'symbol': 'MNQ', 'size': 2},
            {'symbol': 'MNQ', 'size': 2},
            {'symbol': 'MNQ', 'size': 2}
        ]

        risk_assessment = risk_manager.assess_trade(
            symbol="MNQ",
            direction="LONG",
            entry_price=18500,
            account_balance=100000,
            atr=85
        )

        # Should reject - max 3 positions
        assert risk_assessment.approved == False
        assert "Max positions" in risk_assessment.reason

    def test_atr_stop_loss(self, risk_manager):
        """Test ATR-based stop loss calculation"""
        stop = risk_manager._calculate_stop_loss(
            entry_price=18500,
            direction="LONG",
            atr=85,
            multiplier=2
        )

        # LONG: entry - (ATR * 2)
        expected = 18500 - (85 * 2)
        assert stop == expected


class TestMonitoring:
    """Tests for monitoring system"""

    @pytest.fixture
    def monitoring(self):
        """Create monitoring system"""
        from core.monitoring import EarlyWarningSystem
        return EarlyWarningSystem(check_interval=1)

    def test_monitoring_initialization(self, monitoring):
        """Test monitoring initializes correctly"""
        assert monitoring.running == False
        assert monitoring.thresholds['cpu_warning'] == 80
        assert monitoring.thresholds['cpu_critical'] == 95

    def test_resource_check(self, monitoring):
        """Test system resource check"""
        result = monitoring._check_system_resources()

        assert result.component == "system_resources"
        assert result.status in ['healthy', 'degraded', 'unhealthy']
        assert 'cpu_percent' in result.metrics
        assert 'memory_percent' in result.metrics

    def test_alert_triggering(self, monitoring):
        """Test alert system"""
        from core.monitoring import AlertSeverity

        alerts_received = []

        def test_callback(alert):
            alerts_received.append(alert)

        monitoring.alert_callbacks.append(test_callback)

        # Trigger test alert
        monitoring._trigger_alert(
            AlertSeverity.WARNING,
            "test",
            "Test alert message",
            {}
        )

        assert len(alerts_received) == 1
        assert alerts_received[0].severity == AlertSeverity.WARNING
        assert alerts_received[0].component == "test"


class TestAutonomousBrain:
    """Tests for autonomous brain decision loop"""

    @pytest.fixture
    def brain(self):
        """Create autonomous brain"""
        with patch('core.autonomous_brain.get_brain'):
            from core.autonomous_brain import AutonomousBrain
            return AutonomousBrain()

    def test_initialization(self, brain):
        """Test autonomous brain initializes"""
        assert brain.cycle_count == 0
        assert brain.successful_decisions == 0
        assert brain.failed_decisions == 0

    def test_text_based_reasoning(self, brain):
        """Test text-based reasoning fallback"""
        context_parts = ["Goal: Test goal", "Observation: Test observation"]

        reasoning = brain._text_based_reasoning(context_parts)

        assert "Test goal" in reasoning or "autonomous" in reasoning.lower()
        assert len(reasoning) > 0

    def test_decision_confidence_levels(self, brain):
        """Test decision making at different confidence levels"""
        # High confidence
        analysis_high = {'confidence': 0.9, 'reasoning': 'High confidence test'}
        decision_high = brain._decide(analysis_high)
        assert decision_high['type'] == 'autonomous'

        # Medium confidence
        analysis_med = {'confidence': 0.7, 'reasoning': 'Medium confidence test'}
        decision_med = brain._decide(analysis_med)
        assert decision_med['type'] == 'cautious'

        # Low confidence
        analysis_low = {'confidence': 0.3, 'reasoning': 'Low confidence test'}
        decision_low = brain._decide(analysis_low)
        assert decision_low['type'] == 'conservative'


class TestIntegration:
    """Integration tests for full workflows"""

    def test_vision_to_memory_flow(self):
        """Test vision analysis → memory storage flow"""
        with patch('core.brain.UnifiedInference'):
            from core.brain import get_brain
            from core.autonomous_memory import remember_short

            brain = get_brain()
            brain.model.inference = Mock(return_value={
                'answer': 'Integration test answer',
                'thinking': 'Integration test reasoning'
            })

            # Analyze image
            result = brain.analyze("test.jpg", "Test question?")

            # Store in memory
            remember_short("observation", f"Vision: {result['answer']}")

            # Recall from memory
            from core.autonomous_memory import recall_recent
            recent = recall_recent(limit=1)

            assert len(recent) > 0
            assert "Integration test answer" in recent[0].content

    def test_monitoring_with_brain(self):
        """Test monitoring system detecting brain issues"""
        from core.monitoring import EarlyWarningSystem

        monitoring = EarlyWarningSystem(check_interval=1)

        # Check brain health
        health = monitoring._check_brain_health()

        assert health.component == "brain"
        assert health.status in ['healthy', 'unhealthy', 'degraded']


# Performance tests
class TestPerformance:
    """Performance regression tests"""

    def test_memory_query_speed(self, tmp_path):
        """Test memory queries are fast enough"""
        import time
        from core.autonomous_memory import ShortTermMemoryStore

        db_path = tmp_path / "perf_test.db"
        store = ShortTermMemoryStore(db_path=str(db_path))

        # Add 100 memories
        for i in range(100):
            store.add("observation", f"Performance test {i}")

        # Query should be fast
        start = time.time()
        memories = store.get_recent(limit=10)
        elapsed = time.time() - start

        assert elapsed < 0.1  # Should be < 100ms
        assert len(memories) == 10

    def test_risk_calculation_speed(self):
        """Test risk calculations are fast"""
        import time
        from trading.risk_manager import RiskManager

        risk_mgr = RiskManager()

        start = time.time()
        for _ in range(100):
            size = risk_mgr.calculate_position_size(
                account_balance=100000,
                risk_percent=1.0,
                stop_loss_points=50
            )
        elapsed = time.time() - start

        # 100 calculations in < 100ms
        assert elapsed < 0.1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
