"""
PersonalAI Production Monitoring & Early Warning System

Critical monitoring for production deployment:
- Health checks
- Performance metrics
- Error tracking
- Early warning alerts
- Anomaly detection
"""

import logging
import time
import psutil
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import sys

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.autonomous_memory import remember_short, remember_long

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class HealthCheck:
    """Health check result"""
    component: str
    status: str  # healthy, degraded, unhealthy
    message: str
    timestamp: datetime
    metrics: Dict


@dataclass
class Alert:
    """System alert"""
    severity: AlertSeverity
    component: str
    message: str
    timestamp: datetime
    metadata: Dict


class EarlyWarningSystem:
    """
    Production monitoring and early warning system

    Monitors:
    - System health (CPU, memory, disk)
    - Component health (brain, worker, trader)
    - Performance metrics
    - Error rates
    - Anomalies

    Alerts on:
    - Component failures
    - Performance degradation
    - Resource exhaustion
    - Unusual patterns
    """

    def __init__(self,
                 check_interval: int = 60,
                 alert_callbacks: Optional[List[Callable]] = None):
        """
        Initialize early warning system

        Args:
            check_interval: Seconds between health checks
            alert_callbacks: Functions to call when alerts triggered
        """
        self.check_interval = check_interval
        self.alert_callbacks = alert_callbacks or []

        # State tracking
        self.running = False
        self.last_health_check = None
        self.health_history = []
        self.alerts = []

        # Metrics
        self.metrics = {
            'cpu_percent': [],
            'memory_percent': [],
            'disk_percent': [],
            'error_count': 0,
            'warning_count': 0,
            'uptime_start': datetime.now()
        }

        # Thresholds
        self.thresholds = {
            'cpu_warning': 80,      # 80% CPU = warning
            'cpu_critical': 95,     # 95% CPU = critical
            'memory_warning': 80,
            'memory_critical': 90,
            'disk_warning': 85,
            'disk_critical': 95,
            'error_rate_warning': 5,   # 5 errors/min
            'error_rate_critical': 10   # 10 errors/min
        }

        # Component status
        self.components = {
            'brain': {'status': 'unknown', 'last_check': None},
            'autonomous_brain': {'status': 'unknown', 'last_check': None},
            'worker': {'status': 'unknown', 'last_check': None},
            'trader': {'status': 'unknown', 'last_check': None},
            'memory': {'status': 'unknown', 'last_check': None}
        }

        logger.info("🚨 Early Warning System initialized")

    def start(self):
        """Start monitoring"""
        self.running = True

        remember_short("action", "Early Warning System started")
        logger.info("🚀 Early Warning System starting...")

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()

        logger.info("✅ Early Warning System active")

    def stop(self):
        """Stop monitoring"""
        self.running = False
        remember_short("observation", "Early Warning System stopped")
        logger.info("🛑 Early Warning System stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""

        while self.running:
            try:
                # Run health checks
                health_results = self._run_health_checks()

                # Analyze metrics
                self._analyze_metrics()

                # Check for anomalies
                self._detect_anomalies()

                # Store history
                self.last_health_check = datetime.now()
                self.health_history.append({
                    'timestamp': self.last_health_check,
                    'results': health_results
                })

                # Trim history (keep last 24 hours)
                cutoff = datetime.now() - timedelta(hours=24)
                self.health_history = [
                    h for h in self.health_history
                    if h['timestamp'] > cutoff
                ]

                # Sleep until next check
                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                self._trigger_alert(
                    AlertSeverity.CRITICAL,
                    "monitoring",
                    f"Monitoring loop failed: {e}",
                    {}
                )
                time.sleep(self.check_interval * 2)

    def _run_health_checks(self) -> List[HealthCheck]:
        """Run all health checks"""

        results = []

        # System resources
        results.append(self._check_system_resources())

        # Brain health
        results.append(self._check_brain_health())

        # Worker health
        results.append(self._check_worker_health())

        # Trader health
        results.append(self._check_trader_health())

        # Memory health
        results.append(self._check_memory_health())

        return results

    def _check_system_resources(self) -> HealthCheck:
        """Check CPU, memory, disk"""

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent

            # Store metrics
            self.metrics['cpu_percent'].append(cpu_percent)
            self.metrics['memory_percent'].append(memory_percent)
            self.metrics['disk_percent'].append(disk_percent)

            # Trim metrics (last 1000 samples)
            for key in ['cpu_percent', 'memory_percent', 'disk_percent']:
                if len(self.metrics[key]) > 1000:
                    self.metrics[key] = self.metrics[key][-1000:]

            # Determine status
            if (cpu_percent > self.thresholds['cpu_critical'] or
                memory_percent > self.thresholds['memory_critical'] or
                disk_percent > self.thresholds['disk_critical']):
                status = 'unhealthy'

                # Trigger critical alert
                self._trigger_alert(
                    AlertSeverity.CRITICAL,
                    "system_resources",
                    f"Critical resource usage: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%, Disk {disk_percent:.1f}%",
                    {
                        'cpu': cpu_percent,
                        'memory': memory_percent,
                        'disk': disk_percent
                    }
                )

            elif (cpu_percent > self.thresholds['cpu_warning'] or
                  memory_percent > self.thresholds['memory_warning'] or
                  disk_percent > self.thresholds['disk_warning']):
                status = 'degraded'

                # Trigger warning
                self._trigger_alert(
                    AlertSeverity.WARNING,
                    "system_resources",
                    f"High resource usage: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%, Disk {disk_percent:.1f}%",
                    {
                        'cpu': cpu_percent,
                        'memory': memory_percent,
                        'disk': disk_percent
                    }
                )
            else:
                status = 'healthy'

            return HealthCheck(
                component="system_resources",
                status=status,
                message=f"CPU: {cpu_percent:.1f}%, Memory: {memory_percent:.1f}%, Disk: {disk_percent:.1f}%",
                timestamp=datetime.now(),
                metrics={
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'disk_percent': disk_percent
                }
            )

        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return HealthCheck(
                component="system_resources",
                status="unhealthy",
                message=f"Check failed: {e}",
                timestamp=datetime.now(),
                metrics={}
            )

    def _check_brain_health(self) -> HealthCheck:
        """Check RoboBrain health"""

        try:
            from core.brain import get_brain

            brain = get_brain()

            if brain.is_ready:
                status = 'healthy'
                message = f"Brain ready: {brain.model_id}"
            else:
                status = 'unhealthy'
                message = "Brain not initialized"

                self._trigger_alert(
                    AlertSeverity.CRITICAL,
                    "brain",
                    "RoboBrain not ready - vision capabilities disabled",
                    {}
                )

            self.components['brain']['status'] = status
            self.components['brain']['last_check'] = datetime.now()

            return HealthCheck(
                component="brain",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={'ready': brain.is_ready}
            )

        except Exception as e:
            logger.error(f"Brain health check failed: {e}")

            self._trigger_alert(
                AlertSeverity.CRITICAL,
                "brain",
                f"Brain health check failed: {e}",
                {}
            )

            return HealthCheck(
                component="brain",
                status="unhealthy",
                message=f"Check failed: {e}",
                timestamp=datetime.now(),
                metrics={}
            )

    def _check_worker_health(self) -> HealthCheck:
        """Check autonomous worker health"""

        try:
            # Check if worker is running by checking memory activity
            from core.autonomous_memory import recall_recent

            recent = recall_recent(limit=5)

            if recent:
                latest = recent[-1]
                time_since_activity = (datetime.now() - datetime.fromisoformat(latest.timestamp)).total_seconds()

                if time_since_activity < 300:  # Active in last 5 min
                    status = 'healthy'
                    message = f"Worker active (last activity: {int(time_since_activity)}s ago)"
                elif time_since_activity < 600:  # Active in last 10 min
                    status = 'degraded'
                    message = f"Worker slow (last activity: {int(time_since_activity)}s ago)"

                    self._trigger_alert(
                        AlertSeverity.WARNING,
                        "worker",
                        f"Worker appears slow - no activity for {int(time_since_activity)}s",
                        {'time_since_activity': time_since_activity}
                    )
                else:
                    status = 'unhealthy'
                    message = f"Worker inactive (last activity: {int(time_since_activity)}s ago)"

                    self._trigger_alert(
                        AlertSeverity.CRITICAL,
                        "worker",
                        f"Worker appears stopped - no activity for {int(time_since_activity)}s",
                        {'time_since_activity': time_since_activity}
                    )
            else:
                status = 'unknown'
                message = "No worker activity detected"

            self.components['worker']['status'] = status
            self.components['worker']['last_check'] = datetime.now()

            return HealthCheck(
                component="worker",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={}
            )

        except Exception as e:
            logger.error(f"Worker health check failed: {e}")
            return HealthCheck(
                component="worker",
                status="unknown",
                message=f"Check failed: {e}",
                timestamp=datetime.now(),
                metrics={}
            )

    def _check_trader_health(self) -> HealthCheck:
        """Check autonomous trader health"""

        try:
            # Check trader memory activity
            from core.autonomous_memory import recall_relevant

            trader_memories = recall_relevant("trading strategy", limit=5)

            if trader_memories:
                status = 'healthy'
                message = f"Trader active ({len(trader_memories)} recent strategies)"
            else:
                status = 'unknown'
                message = "No trader activity"

            self.components['trader']['status'] = status
            self.components['trader']['last_check'] = datetime.now()

            return HealthCheck(
                component="trader",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={}
            )

        except Exception as e:
            logger.error(f"Trader health check failed: {e}")
            return HealthCheck(
                component="trader",
                status="unknown",
                message=f"Check failed: {e}",
                timestamp=datetime.now(),
                metrics={}
            )

    def _check_memory_health(self) -> HealthCheck:
        """Check memory system health"""

        try:
            from core.autonomous_memory import get_short_term_memory, get_long_term_memory

            short_mem = get_short_term_memory()
            long_mem = get_long_term_memory()

            # Check if memory systems are accessible
            if short_mem and long_mem:
                status = 'healthy'
                message = "Memory systems operational"
            elif short_mem:
                status = 'degraded'
                message = "Only short-term memory available"

                self._trigger_alert(
                    AlertSeverity.WARNING,
                    "memory",
                    "Long-term memory unavailable - learning disabled",
                    {}
                )
            else:
                status = 'unhealthy'
                message = "Memory systems failed"

                self._trigger_alert(
                    AlertSeverity.CRITICAL,
                    "memory",
                    "Memory systems failed - cannot store/recall data",
                    {}
                )

            self.components['memory']['status'] = status
            self.components['memory']['last_check'] = datetime.now()

            return HealthCheck(
                component="memory",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={
                    'short_term': short_mem is not None,
                    'long_term': long_mem is not None and long_mem.enabled
                }
            )

        except Exception as e:
            logger.error(f"Memory health check failed: {e}")
            return HealthCheck(
                component="memory",
                status="unhealthy",
                message=f"Check failed: {e}",
                timestamp=datetime.now(),
                metrics={}
            )

    def _analyze_metrics(self):
        """Analyze metrics for trends"""

        # Check for sustained high CPU
        if len(self.metrics['cpu_percent']) >= 10:
            recent_cpu = self.metrics['cpu_percent'][-10:]
            avg_cpu = sum(recent_cpu) / len(recent_cpu)

            if avg_cpu > self.thresholds['cpu_warning']:
                self._trigger_alert(
                    AlertSeverity.WARNING,
                    "performance",
                    f"Sustained high CPU: {avg_cpu:.1f}% average over last 10 checks",
                    {'avg_cpu': avg_cpu}
                )

        # Check for memory leak
        if len(self.metrics['memory_percent']) >= 20:
            # Check if memory is steadily increasing
            recent_mem = self.metrics['memory_percent'][-20:]
            if all(recent_mem[i] <= recent_mem[i+1] for i in range(len(recent_mem)-1)):
                self._trigger_alert(
                    AlertSeverity.WARNING,
                    "performance",
                    "Possible memory leak detected - memory steadily increasing",
                    {'memory_trend': recent_mem}
                )

    def _detect_anomalies(self):
        """Detect unusual patterns"""

        # Check for no activity (system frozen?)
        if self.health_history:
            last_check = self.health_history[-1]['timestamp']
            time_since = (datetime.now() - last_check).total_seconds()

            if time_since > self.check_interval * 3:
                self._trigger_alert(
                    AlertSeverity.EMERGENCY,
                    "system",
                    f"System appears frozen - no health checks for {int(time_since)}s",
                    {'time_since_check': time_since}
                )

    def _trigger_alert(self,
                      severity: AlertSeverity,
                      component: str,
                      message: str,
                      metadata: Dict):
        """Trigger alert"""

        alert = Alert(
            severity=severity,
            component=component,
            message=message,
            timestamp=datetime.now(),
            metadata=metadata
        )

        self.alerts.append(alert)

        # Log alert
        if severity == AlertSeverity.EMERGENCY:
            logger.critical(f"🚨 EMERGENCY: [{component}] {message}")
        elif severity == AlertSeverity.CRITICAL:
            logger.error(f"❌ CRITICAL: [{component}] {message}")
        elif severity == AlertSeverity.WARNING:
            logger.warning(f"⚠️ WARNING: [{component}] {message}")
        else:
            logger.info(f"ℹ️ INFO: [{component}] {message}")

        # Store in memory
        if severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
            remember_long(
                type="alert",
                content=f"{severity.value.upper()}: {component} - {message}",
                tags=["monitoring", "alert", severity.value, component],
                importance=9 if severity == AlertSeverity.EMERGENCY else 8
            )

        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

    def get_system_status(self) -> Dict:
        """Get overall system status"""

        uptime = datetime.now() - self.metrics['uptime_start']

        # Determine overall status
        component_statuses = [c['status'] for c in self.components.values()]
        if 'unhealthy' in component_statuses:
            overall_status = 'unhealthy'
        elif 'degraded' in component_statuses:
            overall_status = 'degraded'
        elif 'unknown' in component_statuses:
            overall_status = 'unknown'
        else:
            overall_status = 'healthy'

        # Count recent alerts
        recent_alerts = [a for a in self.alerts if (datetime.now() - a.timestamp).total_seconds() < 3600]

        return {
            'overall_status': overall_status,
            'uptime_seconds': uptime.total_seconds(),
            'last_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'components': self.components,
            'metrics': {
                'cpu_current': self.metrics['cpu_percent'][-1] if self.metrics['cpu_percent'] else 0,
                'memory_current': self.metrics['memory_percent'][-1] if self.metrics['memory_percent'] else 0,
                'disk_current': self.metrics['disk_percent'][-1] if self.metrics['disk_percent'] else 0
            },
            'alerts': {
                'total': len(self.alerts),
                'recent_1h': len(recent_alerts),
                'by_severity': {
                    'emergency': len([a for a in recent_alerts if a.severity == AlertSeverity.EMERGENCY]),
                    'critical': len([a for a in recent_alerts if a.severity == AlertSeverity.CRITICAL]),
                    'warning': len([a for a in recent_alerts if a.severity == AlertSeverity.WARNING]),
                    'info': len([a for a in recent_alerts if a.severity == AlertSeverity.INFO])
                }
            }
        }

    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """Get recent alerts"""
        return sorted(self.alerts, key=lambda a: a.timestamp, reverse=True)[:limit]


# Singleton instance
_monitoring_instance: Optional[EarlyWarningSystem] = None

def get_monitoring_system() -> EarlyWarningSystem:
    """Get or create monitoring system singleton"""
    global _monitoring_instance
    if _monitoring_instance is None:
        _monitoring_instance = EarlyWarningSystem()
    return _monitoring_instance


# Test
if __name__ == "__main__":
    print("🚨 Early Warning System Test\n")
    print("=" * 60)

    monitoring = get_monitoring_system()

    print("\nStarting monitoring for 30 seconds...")
    monitoring.start()

    time.sleep(30)

    status = monitoring.get_system_status()
    print(f"\nSystem Status: {status['overall_status']}")
    print(f"Uptime: {status['uptime_seconds']:.1f}s")
    print(f"Total alerts: {status['alerts']['total']}")

    print("\nRecent alerts:")
    for alert in monitoring.get_recent_alerts(5):
        print(f"  [{alert.severity.value}] {alert.component}: {alert.message}")

    monitoring.stop()

    print("\n" + "=" * 60)
    print("✅ Monitoring test complete!")
