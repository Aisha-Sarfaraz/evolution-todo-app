"""Utility modules."""

from src.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    create_email_verification_token,
    check_account_lockout,
    record_failed_signin,
    record_successful_signin,
)
from src.utils.errors import (
    ErrorCode,
    ErrorResponse,
    format_error,
    raise_not_found,
    raise_forbidden,
    raise_unauthorized,
    raise_validation_error,
    raise_duplicate_error,
)
from src.utils.logging import (
    AuditEventType,
    AuditLogLevel,
    get_audit_logger,
    log_signin_success,
    log_signin_failed,
    log_signup_success,
    log_signup_failed,
    log_unauthorized_access,
    log_forbidden_access,
    log_account_locked,
    log_password_change,
    log_password_reset_request,
    log_password_reset,
    log_email_verification,
    log_rate_limited,
)

__all__ = [
    # Auth utilities
    "hash_password", "verify_password",
    "create_access_token", "create_refresh_token",
    "create_password_reset_token", "create_email_verification_token",
    "check_account_lockout", "record_failed_signin", "record_successful_signin",
    # Error utilities
    "ErrorCode", "ErrorResponse", "format_error",
    "raise_not_found", "raise_forbidden", "raise_unauthorized",
    "raise_validation_error", "raise_duplicate_error",
    # Audit logging utilities
    "AuditEventType", "AuditLogLevel", "get_audit_logger",
    "log_signin_success", "log_signin_failed",
    "log_signup_success", "log_signup_failed",
    "log_unauthorized_access", "log_forbidden_access",
    "log_account_locked", "log_password_change",
    "log_password_reset_request", "log_password_reset",
    "log_email_verification", "log_rate_limited",
]
