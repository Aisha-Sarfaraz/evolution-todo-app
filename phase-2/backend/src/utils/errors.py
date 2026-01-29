"""Error response formatting utilities for consistent API error responses."""

from typing import Any
from enum import Enum

from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorCode(str, Enum):
    """Standardized error codes for API responses.

    Error codes provide machine-readable identifiers for error handling
    in frontend applications and API clients.
    """
    # Authentication errors (401)
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

    # Authorization errors (403)
    FORBIDDEN = "FORBIDDEN"
    EMAIL_NOT_VERIFIED = "EMAIL_NOT_VERIFIED"

    # Resource errors (404)
    NOT_FOUND = "NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    CATEGORY_NOT_FOUND = "CATEGORY_NOT_FOUND"
    TAG_NOT_FOUND = "TAG_NOT_FOUND"

    # Validation errors (400/422)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    TAG_ALREADY_EXISTS = "TAG_ALREADY_EXISTS"
    CATEGORY_ALREADY_EXISTS = "CATEGORY_ALREADY_EXISTS"
    DUPLICATE_TAG = "DUPLICATE_TAG"
    DUPLICATE_CATEGORY = "DUPLICATE_CATEGORY"

    # Rate limiting (429)
    RATE_LIMITED = "RATE_LIMITED"

    # Account security (423)
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"

    # Server errors (500)
    SERVER_ERROR = "SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"


class ErrorResponse(BaseModel):
    """Standardized error response schema.

    Attributes:
        error_code: Machine-readable error code (e.g., "VALIDATION_ERROR")
        detail: Human-readable error message
        field: Optional field name for validation errors

    Example:
        {
            "error_code": "VALIDATION_ERROR",
            "detail": "Title is required",
            "field": "title"
        }
    """
    error_code: str
    detail: str
    field: str | None = None


class ValidationErrorDetail(BaseModel):
    """Detailed validation error for a specific field.

    Attributes:
        field: Field name that failed validation
        message: Human-readable error message
        value: The invalid value (optional, may be omitted for security)
    """
    field: str
    message: str
    value: Any | None = None


class ValidationErrorResponse(BaseModel):
    """Response schema for multiple validation errors.

    Attributes:
        error_code: Always "VALIDATION_ERROR"
        detail: Summary message
        errors: List of field-specific validation errors

    Example:
        {
            "error_code": "VALIDATION_ERROR",
            "detail": "Request validation failed",
            "errors": [
                {"field": "title", "message": "Title is required"},
                {"field": "email", "message": "Invalid email format"}
            ]
        }
    """
    error_code: str = ErrorCode.VALIDATION_ERROR
    detail: str = "Request validation failed"
    errors: list[ValidationErrorDetail]


def format_error(
    error_code: str | ErrorCode,
    detail: str,
    field: str | None = None
) -> dict[str, Any]:
    """Format a standardized error response dictionary.

    Args:
        error_code: Error code string or ErrorCode enum
        detail: Human-readable error message
        field: Optional field name for validation errors

    Returns:
        dict: Error response with error_code, detail, and optional field

    Example:
        >>> format_error(ErrorCode.VALIDATION_ERROR, "Title is required", "title")
        {"error_code": "VALIDATION_ERROR", "detail": "Title is required", "field": "title"}
    """
    error: dict[str, Any] = {
        "error_code": error_code.value if isinstance(error_code, ErrorCode) else error_code,
        "detail": detail,
    }

    if field is not None:
        error["field"] = field

    return error


def format_validation_errors(
    errors: list[tuple[str, str]]
) -> dict[str, Any]:
    """Format multiple validation errors into response dictionary.

    Args:
        errors: List of (field, message) tuples

    Returns:
        dict: Validation error response with errors list

    Example:
        >>> format_validation_errors([("title", "Required"), ("email", "Invalid")])
        {
            "error_code": "VALIDATION_ERROR",
            "detail": "Request validation failed",
            "errors": [
                {"field": "title", "message": "Required"},
                {"field": "email", "message": "Invalid"}
            ]
        }
    """
    return {
        "error_code": ErrorCode.VALIDATION_ERROR.value,
        "detail": "Request validation failed",
        "errors": [{"field": field, "message": message} for field, message in errors]
    }


def raise_not_found(
    resource: str,
    resource_id: str | None = None
) -> None:
    """Raise 404 Not Found HTTPException.

    Args:
        resource: Resource type (e.g., "Task", "User", "Category")
        resource_id: Optional resource ID for detailed message

    Raises:
        HTTPException: 404 Not Found with formatted error

    Example:
        >>> raise_not_found("Task", "123e4567-e89b-12d3-a456-426614174000")
        # Raises HTTPException with detail: "Task not found"
    """
    error_code_map = {
        "Task": ErrorCode.TASK_NOT_FOUND,
        "User": ErrorCode.USER_NOT_FOUND,
        "Category": ErrorCode.CATEGORY_NOT_FOUND,
        "Tag": ErrorCode.TAG_NOT_FOUND,
    }

    error_code = error_code_map.get(resource, ErrorCode.NOT_FOUND)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=format_error(
            error_code,
            f"{resource} not found"
        )
    )


def raise_forbidden(
    detail: str = "Cannot access other users' resources"
) -> None:
    """Raise 403 Forbidden HTTPException.

    Args:
        detail: Human-readable error message

    Raises:
        HTTPException: 403 Forbidden with formatted error
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=format_error(ErrorCode.FORBIDDEN, detail)
    )


def raise_unauthorized(
    error_code: ErrorCode = ErrorCode.AUTHENTICATION_REQUIRED,
    detail: str = "Valid authentication token required"
) -> None:
    """Raise 401 Unauthorized HTTPException.

    Args:
        error_code: Specific authentication error code
        detail: Human-readable error message

    Raises:
        HTTPException: 401 Unauthorized with formatted error and WWW-Authenticate header
    """
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=format_error(error_code, detail),
        headers={"WWW-Authenticate": "Bearer"}
    )


def raise_validation_error(
    detail: str,
    field: str | None = None
) -> None:
    """Raise 400 Bad Request HTTPException for validation errors.

    Args:
        detail: Human-readable error message
        field: Optional field name that failed validation

    Raises:
        HTTPException: 400 Bad Request with formatted error
    """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=format_error(ErrorCode.VALIDATION_ERROR, detail, field)
    )


def raise_duplicate_error(
    resource: str,
    field: str,
    value: str | None = None
) -> None:
    """Raise 409 Conflict HTTPException for duplicate entries.

    Args:
        resource: Resource type (e.g., "User", "Tag")
        field: Field that has duplicate value
        value: Optional duplicate value (omit for security)

    Raises:
        HTTPException: 409 Conflict with formatted error
    """
    error_code_map = {
        ("User", "email"): ErrorCode.EMAIL_ALREADY_EXISTS,
        ("Tag", "name"): ErrorCode.TAG_ALREADY_EXISTS,
        ("Category", "name"): ErrorCode.CATEGORY_ALREADY_EXISTS,
    }

    error_code = error_code_map.get((resource, field), ErrorCode.DUPLICATE_ENTRY)
    detail = f"{resource} with this {field} already exists"

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=format_error(error_code, detail, field)
    )


def raise_rate_limited(
    retry_after: int = 60
) -> None:
    """Raise 429 Too Many Requests HTTPException.

    Args:
        retry_after: Seconds until client can retry

    Raises:
        HTTPException: 429 Too Many Requests with Retry-After header
    """
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=format_error(
            ErrorCode.RATE_LIMITED,
            f"Too many requests. Please retry after {retry_after} seconds."
        ),
        headers={"Retry-After": str(retry_after)}
    )
