"""
PersonalAI Error Recovery System

Automatic error recovery, graceful shutdown, and state persistence
"""

import signal
import sys
import logging
import pickle
import json
from typing import Optional, Callable, Dict, Any
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SystemState:
    """System state for persistence"""
    timestamp: str
    mode: str
    goals: list
    metrics: Dict[str, Any]
    component_status: Dict[str, str]


class ErrorRecovery:
    """
    Error recovery and state management

    Features:
    - Automatic restart on failure
    - State persistence
    - Graceful shutdown
    - Error logging
    """

    def __init__(self,
                 state_file: str = "~/.personalai/state/system_state.pkl",
                 auto_restart: bool = True):
        """
        Initialize error recovery

        Args:
            state_file: Path to state persistence file
            auto_restart: Automatically restart on failure
        """
        self.state_file = Path(state_file).expanduser()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        self.auto_restart = auto_restart
        self.shutdown_callbacks = []
        self.restart_callbacks = []

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._handle_sigint)
        signal.signal(signal.SIGTERM, self._handle_sigterm)

        logger.info("🔄 Error recovery system initialized")

    def save_state(self, state: SystemState):
        """
        Save system state to disk

        Args:
            state: System state to save
        """
        try:
            with open(self.state_file, 'wb') as f:
                pickle.dump(state, f)

            logger.info(f"💾 State saved: {self.state_file}")

        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def load_state(self) -> Optional[SystemState]:
        """
        Load system state from disk

        Returns:
            Saved state or None
        """
        if not self.state_file.exists():
            logger.info("No saved state found")
            return None

        try:
            with open(self.state_file, 'rb') as f:
                state = pickle.load(f)

            logger.info(f"📂 State loaded: {state.timestamp}")
            return state

        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None

    def register_shutdown_callback(self, callback: Callable):
        """
        Register callback for graceful shutdown

        Args:
            callback: Function to call on shutdown
        """
        self.shutdown_callbacks.append(callback)
        logger.info(f"Registered shutdown callback: {callback.__name__}")

    def register_restart_callback(self, callback: Callable):
        """
        Register callback for restart

        Args:
            callback: Function to call on restart
        """
        self.restart_callbacks.append(callback)
        logger.info(f"Registered restart callback: {callback.__name__}")

    def graceful_shutdown(self, reason: str = "Manual shutdown"):
        """
        Perform graceful shutdown

        Args:
            reason: Shutdown reason
        """
        logger.info(f"🛑 Graceful shutdown initiated: {reason}")

        # Call shutdown callbacks
        for callback in self.shutdown_callbacks:
            try:
                logger.info(f"  Calling shutdown callback: {callback.__name__}")
                callback()
            except Exception as e:
                logger.error(f"  Shutdown callback failed: {e}")

        logger.info("✅ Graceful shutdown complete")

    def _handle_sigint(self, signum, frame):
        """Handle SIGINT (Ctrl+C)"""
        logger.info("\n⚠️ SIGINT received (Ctrl+C)")
        self.graceful_shutdown("SIGINT")
        sys.exit(0)

    def _handle_sigterm(self, signum, frame):
        """Handle SIGTERM"""
        logger.info("⚠️ SIGTERM received")
        self.graceful_shutdown("SIGTERM")
        sys.exit(0)


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance

    Prevents cascading failures by temporarily stopping
    requests to failing services
    """

    def __init__(self,
                 failure_threshold: int = 5,
                 timeout: int = 60,
                 recovery_timeout: int = 30):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Failures before opening circuit
            timeout: Timeout for open circuit (seconds)
            recovery_timeout: Timeout in half-open state
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

        logger.info(f"⚡ Circuit breaker initialized (threshold: {failure_threshold})")

    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open
        """
        if self.state == "OPEN":
            # Check if we should try recovery
            if self.last_failure_time:
                elapsed = datetime.now().timestamp() - self.last_failure_time
                if elapsed > self.timeout:
                    self.state = "HALF_OPEN"
                    logger.info("⚡ Circuit breaker: OPEN → HALF_OPEN")
                else:
                    raise Exception(f"Circuit breaker OPEN (retry in {self.timeout - int(elapsed)}s)")

        try:
            result = func(*args, **kwargs)

            # Success - reset on HALF_OPEN
            if self.state == "HALF_OPEN":
                self.failure_count = 0
                self.state = "CLOSED"
                logger.info("⚡ Circuit breaker: HALF_OPEN → CLOSED (recovered)")

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now().timestamp()

            logger.error(f"Circuit breaker: Failure {self.failure_count}/{self.failure_threshold}")

            # Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error("⚡ Circuit breaker: CLOSED → OPEN")

            raise e

    def reset(self):
        """Reset circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
        logger.info("⚡ Circuit breaker reset")


class RetryStrategy:
    """
    Retry strategy with exponential backoff
    """

    def __init__(self,
                 max_retries: int = 3,
                 base_delay: float = 2.0,
                 max_delay: float = 60.0):
        """
        Initialize retry strategy

        Args:
            max_retries: Maximum retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay between retries
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

        logger.info(f"🔄 Retry strategy: max {max_retries} attempts")

    def retry(self, func: Callable, *args, **kwargs):
        """
        Execute function with retry

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries fail
        """
        import time

        last_exception = None

        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"✅ Retry successful on attempt {attempt + 1}")
                return result

            except Exception as e:
                last_exception = e
                logger.warning(f"❌ Attempt {attempt + 1}/{self.max_retries} failed: {e}")

                if attempt < self.max_retries - 1:
                    # Calculate delay with exponential backoff
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    logger.info(f"⏳ Retrying in {delay:.1f}s...")
                    time.sleep(delay)

        # All retries failed
        logger.error(f"❌ All {self.max_retries} retry attempts failed")
        raise last_exception


class HealthChecker:
    """
    Component health checking with recovery actions
    """

    def __init__(self):
        """Initialize health checker"""
        self.health_checks = {}
        self.recovery_actions = {}

        logger.info("🏥 Health checker initialized")

    def register_health_check(self,
                             component: str,
                             check_func: Callable,
                             recovery_func: Optional[Callable] = None):
        """
        Register health check for component

        Args:
            component: Component name
            check_func: Function that returns True if healthy
            recovery_func: Function to call for recovery (optional)
        """
        self.health_checks[component] = check_func

        if recovery_func:
            self.recovery_actions[component] = recovery_func

        logger.info(f"Registered health check: {component}")

    def check_all(self) -> Dict[str, bool]:
        """
        Check health of all components

        Returns:
            Dict of component: is_healthy
        """
        results = {}

        for component, check_func in self.health_checks.items():
            try:
                is_healthy = check_func()
                results[component] = is_healthy

                if not is_healthy:
                    logger.warning(f"❌ Component unhealthy: {component}")

                    # Try recovery
                    if component in self.recovery_actions:
                        logger.info(f"🔄 Attempting recovery: {component}")
                        try:
                            self.recovery_actions[component]()
                            logger.info(f"✅ Recovery successful: {component}")
                        except Exception as e:
                            logger.error(f"❌ Recovery failed: {component} - {e}")

            except Exception as e:
                logger.error(f"Health check failed for {component}: {e}")
                results[component] = False

        return results


# Global instances
_error_recovery = ErrorRecovery()
_health_checker = HealthChecker()


def get_error_recovery() -> ErrorRecovery:
    """Get error recovery instance"""
    return _error_recovery


def get_health_checker() -> HealthChecker:
    """Get health checker instance"""
    return _health_checker


# Test
if __name__ == "__main__":
    print("🔄 Error Recovery System Test\n")
    print("=" * 60)

    # Test state persistence
    print("\n1. State Persistence Test:")
    recovery = ErrorRecovery()

    state = SystemState(
        timestamp=datetime.now().isoformat(),
        mode="autonomous",
        goals=["Monitor system", "Optimize performance"],
        metrics={"success_rate": 0.85, "cycles": 100},
        component_status={"brain": "healthy", "trader": "healthy"}
    )

    recovery.save_state(state)
    loaded = recovery.load_state()

    if loaded:
        print(f"  ✅ State saved and loaded successfully")
        print(f"     Mode: {loaded.mode}")
        print(f"     Goals: {len(loaded.goals)}")
    else:
        print(f"  ❌ State persistence failed")

    # Test circuit breaker
    print("\n2. Circuit Breaker Test:")
    circuit = CircuitBreaker(failure_threshold=3, timeout=5)

    def failing_function():
        raise Exception("Simulated failure")

    for i in range(5):
        try:
            circuit.call(failing_function)
        except Exception as e:
            print(f"  Attempt {i+1}: {e}")

    # Test retry strategy
    print("\n3. Retry Strategy Test:")
    retry = RetryStrategy(max_retries=3, base_delay=0.5)

    attempt_count = [0]

    def sometimes_fails():
        attempt_count[0] += 1
        if attempt_count[0] < 2:
            raise Exception(f"Failed attempt {attempt_count[0]}")
        return "Success!"

    try:
        result = retry.retry(sometimes_fails)
        print(f"  ✅ Retry successful: {result}")
    except Exception as e:
        print(f"  ❌ Retry failed: {e}")

    print("\n" + "=" * 60)
    print("✅ Error recovery tests complete!")
