"""Structured audit logging utility.

T085: [US3] Implement audit logging
Structured JSON logging with timestamp, level, user_id, request_id,
event type, IP address, and context.
"""

import json
import logging
import sys
import time
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4
from dataclasses import dataclass, asdict
from enum import Enum


class AuditEventType(str, Enum):
    """Audit log event types."""

    # Authentication events
    SIGNUP = "signup"
    SIGNUP_FAILED = "signup_failed"
    SIGNIN = "signin"
    SIGNIN_FAILED = "signin_failed"
    SIGNOUT = "signout"
    EMAIL_VERIFICATION = "email_verification"
    EMAIL_VERIFICATION_FAILED = "email_verification_failed"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET = "password_reset"
    PASSWORD_RESET_FAILED = "password_reset_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_CHANGE_FAILED = "password_change_failed"

    # Authorization events
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    FORBIDDEN_ACCESS = "forbidden_access"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_INVALID = "token_invalid"

    # Account security events
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    RATE_LIMITED = "rate_limited"

    # Resource access events
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_ACCESS_DENIED = "task_access_denied"

    # Profile events
    PROFILE_UPDATED = "profile_updated"


class AuditLogLevel(str, Enum):
    """Audit log severity levels."""

    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AuditLogEntry:
    """Structured audit log entry."""

    timestamp: str
    level: str
    event_type: str
    user_id: Optional[str]
    request_id: str
    ip_address: Optional[str]
    context: dict[str, Any]

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self), default=str)


class AuditLogger:
    """
    Structured audit logger for security events.

    Outputs JSON-formatted logs for easy parsing and analysis.
    """

    def __init__(self, name: str = "audit"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.INFO)

        # Only add handler if not already configured
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            # Use simple format - the message is already JSON
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def _create_entry(
        self,
        level: AuditLogLevel,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **context: Any,
    ) -> AuditLogEntry:
        """Create a structured audit log entry."""
        return AuditLogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=level.value,
            event_type=event_type.value,
            user_id=user_id,
            request_id=request_id or str(uuid4()),
            ip_address=ip_address,
            context=context,
        )

    def _log(self, entry: AuditLogEntry, level: AuditLogLevel) -> None:
        """Write log entry."""
        json_str = entry.to_json()

        if level == AuditLogLevel.INFO:
            self._logger.info(json_str)
        elif level == AuditLogLevel.WARN:
            self._logger.warning(json_str)
        elif level == AuditLogLevel.ERROR:
            self._logger.error(json_str)
        elif level == AuditLogLevel.CRITICAL:
            self._logger.critical(json_str)

    def info(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **context: Any,
    ) -> None:
        """Log an INFO level audit event."""
        entry = self._create_entry(
            AuditLogLevel.INFO,
            event_type,
            user_id,
            request_id,
            ip_address,
            **context,
        )
        self._log(entry, AuditLogLevel.INFO)

    def warn(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **context: Any,
    ) -> None:
        """Log a WARN level audit event."""
        entry = self._create_entry(
            AuditLogLevel.WARN,
            event_type,
            user_id,
            request_id,
            ip_address,
            **context,
        )
        self._log(entry, AuditLogLevel.WARN)

    def error(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **context: Any,
    ) -> None:
        """Log an ERROR level audit event."""
        entry = self._create_entry(
            AuditLogLevel.ERROR,
            event_type,
            user_id,
            request_id,
            ip_address,
            **context,
        )
        self._log(entry, AuditLogLevel.ERROR)

    def critical(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **context: Any,
    ) -> None:
        """Log a CRITICAL level audit event."""
        entry = self._create_entry(
            AuditLogLevel.CRITICAL,
            event_type,
            user_id,
            request_id,
            ip_address,
            **context,
        )
        self._log(entry, AuditLogLevel.CRITICAL)


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create the audit logger singleton."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


# Convenience functions for common audit events


def log_signin_success(
    user_id: str,
    email: str,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Log successful signin."""
    get_audit_logger().info(
        AuditEventType.SIGNIN,
        user_id=user_id,
        ip_address=ip_address,
        request_id=request_id,
        email=email,
        status="success",
    )


def log_signin_failed(
    email: str,
    reason: str,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Log failed signin attempt."""
    get_audit_logger().warn(
        AuditEventType.SIGNIN_FAILED,
        ip_address=ip_address,
        request_id=request_id,
        email=email,
        reason=reason,
    )


def log_signup_success(
    user_id: str,
    email: str,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Log successful signup."""
    get_audit_logger().info(
        AuditEventType.SIGNUP,
        user_id=user_id,
        ip_address=ip_address,
        request_id=request_id,
        email=email,
        status="success",
    )


def log_signup_failed(
    email: str,
    reason: str,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Log failed signup attempt."""
    get_audit_logger().warn(
        AuditEventType.SIGNUP_FAILED,
        ip_address=ip_address,
        request_id=request_id,
        email=email,
        reason=reason,
    )


def log_unauthorized_access(
    reason: str,
    endpoint: str,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    """Log unauthorized access attempt (401)."""
    get_audit_logger().warn(
        AuditEventType.UNAUTHORIZED_ACCESS,
        user_id=user_id,
        ip_address=ip_address,
        request_id=request_id,
        reason=reason,
        endpoint=endpoint,
    )


def log_forbidden_access(
    user_id: str,
    resource_owner_id: str,
    resource_type: str,
    resource_id: str,
    action: str,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Log forbidden access attempt (403 - cross-user access)."""
    get_audit_logger().warn(
        AuditEventType.FORBIDDEN_ACCESS,
        user_id=user_id,
        ip_address=ip_address,
        request_id=request_id,
        resource_owner_id=resource_owner_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
    )


def log_account_locked(
    email: str,
    failed_attempts: int,
    lockout_minutes: int,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Log account lockout event."""
    get_audit_logger().warn(
        AuditEventType.ACCOUNT_LOCKED,
        ip_address=ip_address,
        request_id=request_id,
        email=email,
        failed_attempts=failed_attempts,
        lockout_minutes=lockout_minutes,
    )


def log_password_change(
    user_id: str,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
    success: bool = True,
) -> None:
    """Log password change event."""
    event_type = AuditEventType.PASSWORD_CHANGE if success else AuditEventType.PASSWORD_CHANGE_FAILED
    level_func = get_audit_logger().info if success else get_audit_logger().warn

    level_func(
        event_type,
        user_id=user_id,
        ip_address=ip_address,
        request_id=request_id,
        status="success" if success else "failed",
    )


def log_password_reset_request(
    email: str,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Log password reset request."""
    get_audit_logger().info(
        AuditEventType.PASSWORD_RESET_REQUEST,
        ip_address=ip_address,
        request_id=request_id,
        email=email,
    )


def log_password_reset(
    user_id: str,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
    success: bool = True,
) -> None:
    """Log password reset completion."""
    event_type = AuditEventType.PASSWORD_RESET if success else AuditEventType.PASSWORD_RESET_FAILED
    level_func = get_audit_logger().info if success else get_audit_logger().warn

    level_func(
        event_type,
        user_id=user_id,
        ip_address=ip_address,
        request_id=request_id,
        status="success" if success else "failed",
    )


def log_email_verification(
    user_id: str,
    email: str,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
    success: bool = True,
) -> None:
    """Log email verification event."""
    event_type = AuditEventType.EMAIL_VERIFICATION if success else AuditEventType.EMAIL_VERIFICATION_FAILED
    level_func = get_audit_logger().info if success else get_audit_logger().warn

    level_func(
        event_type,
        user_id=user_id,
        ip_address=ip_address,
        request_id=request_id,
        email=email,
        status="success" if success else "failed",
    )


def log_rate_limited(
    ip_address: Optional[str] = None,
    user_id: Optional[str] = None,
    endpoint: str = "",
    request_id: Optional[str] = None,
) -> None:
    """Log rate limit event."""
    get_audit_logger().warn(
        AuditEventType.RATE_LIMITED,
        user_id=user_id,
        ip_address=ip_address,
        request_id=request_id,
        endpoint=endpoint,
    )

