"""
PersonalAI Structured Logging

JSON-formatted logging with log rotation for production
"""

import logging
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class JSONFormatter(logging.Formatter):
    """
    JSON log formatter

    Outputs logs in structured JSON format for easy parsing
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""

        log_obj = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'user_id'):
            log_obj['user_id'] = record.user_id

        if hasattr(record, 'component'):
            log_obj['component'] = record.component

        if hasattr(record, 'action'):
            log_obj['action'] = record.action

        return json.dumps(log_obj)


def setup_logging(
    log_file: str = "~/.personalai/logs/personalai.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    level: int = logging.INFO,
    json_format: bool = True
) -> logging.Logger:
    """
    Setup structured logging with rotation

    Args:
        log_file: Log file path
        max_bytes: Max file size before rotation
        backup_count: Number of backup files to keep
        level: Logging level
        json_format: Use JSON formatting

    Returns:
        Configured logger
    """

    # Create log directory
    log_path = Path(log_file).expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger('personalai')
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers = []

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )

    if json_format:
        file_handler.setFormatter(JSONFormatter())
    else:
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

    logger.addHandler(file_handler)

    # Console handler (not JSON for readability)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(console_handler)

    logger.info("Structured logging configured", extra={
        'component': 'logging',
        'log_file': str(log_path),
        'max_bytes': max_bytes,
        'backup_count': backup_count
    })

    return logger


# Convenience functions for contextual logging
def log_user_action(logger: logging.Logger,
                   user_id: str,
                   action: str,
                   details: Optional[Dict[str, Any]] = None):
    """Log user action with context"""

    logger.info(
        f"User action: {action}",
        extra={
            'user_id': user_id,
            'action': action,
            'details': details or {}
        }
    )


def log_component_event(logger: logging.Logger,
                       component: str,
                       event: str,
                       details: Optional[Dict[str, Any]] = None):
    """Log component event with context"""

    logger.info(
        f"Component event: {event}",
        extra={
            'component': component,
            'event': event,
            'details': details or {}
        }
    )


# Test
if __name__ == "__main__":
    print("Structured Logging Test\n")
    print("=" * 60)

    # Setup logging
    logger = setup_logging(
        log_file="/tmp/test_personalai.log",
        json_format=True
    )

    # Test various log levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Test contextual logging
    log_user_action(logger, "user_123", "START_TRADER", {"mode": "paper"})
    log_component_event(logger, "brain", "INFERENCE_COMPLETE", {"duration_ms": 1234})

    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.exception("Exception occurred")

    print("\n" + "=" * 60)
    print("Check /tmp/test_personalai.log for JSON-formatted logs")
