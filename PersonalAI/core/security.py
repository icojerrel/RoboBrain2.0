"""
PersonalAI Security Module

Rate limiting, input validation, and security utilities
"""

import re
import time
import logging
from typing import Dict, Optional, Callable
from functools import wraps
from html import escape
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ===== RATE LIMITING =====

class RateLimiter:
    """
    Rate limiter with configurable limits per user

    Prevents abuse and DDoS attacks
    """

    def __init__(self,
                 default_limit: int = 5,
                 default_window: int = 60):
        """
        Initialize rate limiter

        Args:
            default_limit: Max requests per window
            default_window: Time window in seconds
        """
        self.default_limit = default_limit
        self.default_window = default_window

        # Track requests per user
        self.user_requests: Dict[str, list] = {}

        logger.info(f"🔒 Rate limiter: {default_limit} requests per {default_window}s")

    def is_allowed(self, user_id: str, limit: Optional[int] = None, window: Optional[int] = None) -> tuple[bool, Optional[float]]:
        """
        Check if user is allowed to make request

        Args:
            user_id: User identifier
            limit: Custom limit (optional)
            window: Custom window (optional)

        Returns:
            (allowed: bool, retry_after: float)
        """
        limit = limit or self.default_limit
        window = window or self.default_window

        now = time.time()

        # Initialize user if first request
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []

        # Clean old requests outside window
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if now - req_time < window
        ]

        # Check limit
        if len(self.user_requests[user_id]) >= limit:
            # Calculate retry_after
            oldest = self.user_requests[user_id][0]
            retry_after = window - (now - oldest)
            return False, retry_after

        # Allow request
        self.user_requests[user_id].append(now)
        return True, None

    def reset_user(self, user_id: str):
        """Reset rate limit for user"""
        if user_id in self.user_requests:
            del self.user_requests[user_id]
            logger.info(f"Rate limit reset for user {user_id}")


# Global rate limiter instance
_rate_limiter = RateLimiter(default_limit=10, default_window=60)


def rate_limit(limit: int = 10, window: int = 60):
    """
    Rate limit decorator for async functions

    Usage:
        @rate_limit(limit=5, window=30)
        async def my_command(update, context):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, update, context, *args, **kwargs):
            user_id = str(update.effective_user.id)

            allowed, retry_after = _rate_limiter.is_allowed(user_id, limit, window)

            if not allowed:
                await update.message.reply_text(
                    f"⏳ Too many requests!\n"
                    f"Please wait {int(retry_after)}s before trying again."
                )
                logger.warning(f"Rate limit hit for user {user_id}")
                return

            return await func(self, update, context, *args, **kwargs)
        return wrapper
    return decorator


# ===== INPUT VALIDATION =====

class InputValidator:
    """
    Input validation utilities

    Prevents injection attacks, XSS, and invalid input
    """

    @staticmethod
    def validate_text(text: str,
                     max_length: int = 1000,
                     allow_special: bool = True) -> str:
        """
        Validate and sanitize text input

        Args:
            text: Input text
            max_length: Maximum allowed length
            allow_special: Allow special characters

        Returns:
            Sanitized text

        Raises:
            ValueError: If validation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Length check
        if len(text) > max_length:
            raise ValueError(f"Text too long (max {max_length} characters)")

        # Character validation
        if not allow_special:
            if not re.match(r'^[a-zA-Z0-9\s\-_.,:!?]+$', text):
                raise ValueError("Text contains invalid characters")

        # Sanitize HTML
        sanitized = escape(text)

        return sanitized

    @staticmethod
    def validate_goal(goal: str) -> str:
        """
        Validate goal text

        Args:
            goal: Goal description

        Returns:
            Validated goal

        Raises:
            ValueError: If invalid
        """
        if not goal or not goal.strip():
            raise ValueError("Goal cannot be empty")

        if len(goal) > 500:
            raise ValueError("Goal too long (max 500 characters)")

        # Remove dangerous characters
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onclick=',
            r';\s*DROP',  # SQL injection attempt
            r'--',  # SQL comment
            r'\$\{',  # Template injection
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, goal, re.IGNORECASE):
                raise ValueError("Goal contains potentially dangerous content")

        return escape(goal.strip())

    @staticmethod
    def validate_number(value: str,
                       min_value: Optional[float] = None,
                       max_value: Optional[float] = None) -> float:
        """
        Validate numeric input

        Args:
            value: Numeric string
            min_value: Minimum allowed value
            max_value: Maximum allowed value

        Returns:
            Validated number

        Raises:
            ValueError: If invalid
        """
        try:
            num = float(value)
        except ValueError:
            raise ValueError(f"'{value}' is not a valid number")

        if min_value is not None and num < min_value:
            raise ValueError(f"Value must be >= {min_value}")

        if max_value is not None and num > max_value:
            raise ValueError(f"Value must be <= {max_value}")

        return num

    @staticmethod
    def validate_priority(priority: str) -> int:
        """
        Validate priority level (1-10)

        Args:
            priority: Priority string

        Returns:
            Validated priority

        Raises:
            ValueError: If invalid
        """
        try:
            p = int(priority)
        except ValueError:
            raise ValueError("Priority must be a number")

        if not 1 <= p <= 10:
            raise ValueError("Priority must be between 1 and 10")

        return p

    @staticmethod
    def validate_trading_mode(mode: str) -> str:
        """
        Validate trading mode

        Args:
            mode: Trading mode string

        Returns:
            Validated mode

        Raises:
            ValueError: If invalid
        """
        valid_modes = ['paper', 'live', 'live_confirmed']

        mode_lower = mode.lower().strip()

        if mode_lower not in valid_modes:
            raise ValueError(f"Invalid mode. Must be one of: {', '.join(valid_modes)}")

        return mode_lower

    @staticmethod
    def validate_file_path(path: str, allowed_extensions: Optional[list] = None) -> str:
        """
        Validate file path

        Args:
            path: File path
            allowed_extensions: List of allowed extensions

        Returns:
            Validated path

        Raises:
            ValueError: If invalid
        """
        # Check for path traversal
        if '..' in path or path.startswith('/'):
            raise ValueError("Invalid file path")

        # Check extension
        if allowed_extensions:
            ext = path.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise ValueError(f"File type not allowed. Allowed: {', '.join(allowed_extensions)}")

        return path


# ===== SECRETS MANAGEMENT =====

class SecretsManager:
    """
    Simple secrets manager

    For production, use HashiCorp Vault or AWS Secrets Manager
    """

    def __init__(self):
        """Initialize secrets manager"""
        self._secrets: Dict[str, str] = {}

    def set_secret(self, key: str, value: str):
        """Store secret"""
        self._secrets[key] = value
        logger.info(f"🔐 Secret stored: {key}")

    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve secret"""
        return self._secrets.get(key)

    def delete_secret(self, key: str):
        """Delete secret"""
        if key in self._secrets:
            del self._secrets[key]
            logger.info(f"🔐 Secret deleted: {key}")


# Global secrets manager
_secrets_manager = SecretsManager()


def get_secrets_manager() -> SecretsManager:
    """Get secrets manager instance"""
    return _secrets_manager


# ===== AUDIT LOG =====

class AuditLogger:
    """
    Audit logging for security events

    Tracks who did what and when
    """

    def __init__(self, log_file: str = "audit.log"):
        """Initialize audit logger"""
        self.logger = logging.getLogger("audit")
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_action(self,
                   user_id: str,
                   action: str,
                   details: Optional[Dict] = None,
                   success: bool = True):
        """
        Log user action

        Args:
            user_id: User identifier
            action: Action performed
            details: Additional details
            success: Whether action succeeded
        """
        status = "SUCCESS" if success else "FAILED"
        details_str = str(details) if details else ""

        self.logger.info(
            f"USER={user_id} ACTION={action} STATUS={status} DETAILS={details_str}"
        )

    def log_security_event(self,
                          event_type: str,
                          user_id: Optional[str] = None,
                          details: Optional[Dict] = None):
        """
        Log security event

        Args:
            event_type: Type of security event
            user_id: User involved (if applicable)
            details: Event details
        """
        user_str = f"USER={user_id}" if user_id else "USER=SYSTEM"
        details_str = str(details) if details else ""

        self.logger.warning(
            f"{user_str} SECURITY_EVENT={event_type} DETAILS={details_str}"
        )


# Global audit logger
_audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Get audit logger instance"""
    return _audit_logger


# ===== SANITIZATION UTILITIES =====

def sanitize_sql(value: str) -> str:
    """
    Sanitize value for SQL

    Note: Use parameterized queries instead when possible
    """
    # Remove SQL injection patterns
    dangerous = [
        ';', '--', '/*', '*/', 'xp_', 'sp_',
        'DROP', 'DELETE', 'INSERT', 'UPDATE',
        'EXEC', 'EXECUTE'
    ]

    sanitized = value
    for pattern in dangerous:
        sanitized = sanitized.replace(pattern, '')

    return sanitized


def sanitize_shell(value: str) -> str:
    """
    Sanitize value for shell execution

    Note: Avoid shell execution when possible
    """
    # Remove shell injection patterns
    dangerous = [
        ';', '|', '&', '`', '$', '(', ')',
        '<', '>', '\n', '\r'
    ]

    sanitized = value
    for char in dangerous:
        sanitized = sanitized.replace(char, '')

    return sanitized


# Test
if __name__ == "__main__":
    print("🔒 PersonalAI Security Module\n")
    print("=" * 60)

    # Test rate limiter
    print("\n1. Rate Limiter Test:")
    limiter = RateLimiter(default_limit=3, default_window=10)

    for i in range(5):
        allowed, retry = limiter.is_allowed("test_user")
        if allowed:
            print(f"  Request {i+1}: ✅ Allowed")
        else:
            print(f"  Request {i+1}: ❌ Blocked (retry in {retry:.1f}s)")

    # Test input validation
    print("\n2. Input Validation Test:")
    validator = InputValidator()

    try:
        goal = validator.validate_goal("Monitor system for security issues")
        print(f"  Valid goal: ✅ {goal}")
    except ValueError as e:
        print(f"  Invalid goal: ❌ {e}")

    try:
        bad_goal = validator.validate_goal("<script>alert('xss')</script>")
        print(f"  Bad goal: ❌ Should have been blocked!")
    except ValueError as e:
        print(f"  XSS attempt: ✅ Blocked - {e}")

    # Test audit logging
    print("\n3. Audit Logging Test:")
    audit = AuditLogger()
    audit.log_action("user_123", "START_TRADER", {"mode": "paper"}, success=True)
    audit.log_security_event("RATE_LIMIT_EXCEEDED", "user_456", {"attempts": 10})

    print("\n" + "=" * 60)
    print("✅ Security module tests complete!")
