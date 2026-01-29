"""Authentication API routes.

T039-T047: Auth endpoints for signup, signin, verification, password reset, profile.
T086: Add audit log calls to auth endpoints.

Endpoints:
- POST /api/auth/signup (T039)
- POST /api/auth/verify-email (T040)
- POST /api/auth/signin (T041)
- POST /api/auth/refresh (T042)
- POST /api/auth/signout (T043)
- POST /api/auth/reset-password-request (T044)
- POST /api/auth/reset-password (T045)
- GET /api/{user_id}/profile (T046)
- PUT /api/{user_id}/profile (T047)
"""

import re
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import ValidatedUser, get_current_user, CurrentUser
from src.database import get_session
from src.models.user import User, UserCreate, UserRead, UserUpdate
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
    JWT_SECRET,
    JWT_ALGORITHM,
    LOCKOUT_DURATION_MINUTES,
)
from src.utils.errors import (
    ErrorCode,
    ErrorResponse,
    format_error,
    raise_unauthorized,
    raise_validation_error,
    raise_duplicate_error,
)
from src.utils.logging import (
    log_signin_success,
    log_signin_failed,
    log_signup_success,
    log_signup_failed,
    log_account_locked,
    log_password_change,
    log_password_reset_request,
    log_password_reset,
    log_email_verification,
)

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


router = APIRouter(prefix="/api/auth", tags=["authentication"])
profile_router = APIRouter(tags=["profile"])


# Password validation regex: min 8 chars, 1 uppercase, 1 lowercase, 1 number
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")


def validate_password_strength(password: str) -> bool:
    """Validate password meets strength requirements."""
    return bool(PASSWORD_REGEX.match(password))


# Request/Response schemas

class SignupRequest(BaseModel):
    """Signup request schema."""
    email: EmailStr
    password: str
    password_confirm: str
    name: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not validate_password_strength(v):
            raise ValueError(
                "Password must be at least 8 characters with 1 uppercase, 1 lowercase, and 1 number"
            )
        return v

    @field_validator("password_confirm")
    @classmethod
    def validate_password_confirm(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class SignupResponse(BaseModel):
    """Signup response schema."""
    user_id: str
    message: str


class SigninRequest(BaseModel):
    """Signin request schema."""
    email: EmailStr
    password: str


class SigninResponse(BaseModel):
    """Signin response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600  # 1 hour


class VerifyEmailRequest(BaseModel):
    """Email verification request schema."""
    token: str


class RefreshRequest(BaseModel):
    """Token refresh request schema."""
    refresh_token: str


class ResetPasswordRequestSchema(BaseModel):
    """Password reset request schema."""
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    """Password reset schema."""
    token: str
    new_password: str
    new_password_confirm: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not validate_password_strength(v):
            raise ValueError(
                "Password must be at least 8 characters with 1 uppercase, 1 lowercase, and 1 number"
            )
        return v

    @field_validator("new_password_confirm")
    @classmethod
    def validate_password_confirm(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class ProfileUpdateRequest(BaseModel):
    """Profile update request schema."""
    display_name: str | None = None
    current_password: str | None = None
    new_password: str | None = None

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str | None, info) -> str | None:
        if v is not None:
            if not validate_password_strength(v):
                raise ValueError(
                    "Password must be at least 8 characters with 1 uppercase, 1 lowercase, and 1 number"
                )
            if "current_password" not in info.data or not info.data["current_password"]:
                raise ValueError("Current password required to change password")
        return v


class MessageResponse(BaseModel):
    """Simple message response schema."""
    message: str


# T039: POST /api/auth/signup
@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created successfully", "model": SignupResponse},
        409: {"description": "Email already registered", "model": ErrorResponse},
        422: {"description": "Validation error (password requirements)", "model": ErrorResponse},
    },
    summary="Register new user",
    description="Create a new user account. Email must be unique. "
                "Password must be at least 8 characters with 1 uppercase, 1 lowercase, and 1 number.",
)
async def signup(
    request: SignupRequest,
    http_request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Register a new user account.

    Creates user with hashed password and sends verification email.
    Email must be unique.
    """
    ip_address = get_client_ip(http_request)

    # Check if email already exists
    existing_user = await session.execute(
        select(User).where(User.email == request.email)
    )
    if existing_user.scalar_one_or_none():
        log_signup_failed(request.email, "email_already_exists", ip_address)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=format_error(ErrorCode.EMAIL_ALREADY_EXISTS, "Email already registered", "email")
        )

    # Create user with hashed password
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        display_name=request.name or request.email.split("@")[0],
        email_verified=False,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Generate verification token and send email
    verification_token = create_email_verification_token(user.id, user.email)
    # TODO: Send verification email via email service
    # await send_verification_email(user.email, verification_token)

    # Audit log successful signup
    log_signup_success(str(user.id), request.email, ip_address)

    return SignupResponse(
        user_id=str(user.id),
        message="Registration successful. Please check your email to verify your account."
    )


# T040: POST /api/auth/verify-email
@router.post(
    "/verify-email",
    response_model=MessageResponse,
    responses={
        200: {"description": "Email verified successfully", "model": MessageResponse},
        401: {"description": "Invalid or expired verification token", "model": ErrorResponse},
        404: {"description": "User not found", "model": ErrorResponse},
    },
    summary="Verify email address",
    description="Verify user email with token sent to their email address. Token expires after 24 hours.",
)
async def verify_email(
    request: VerifyEmailRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Verify user email address with token."""
    try:
        payload = jwt.decode(
            request.token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        if payload.get("token_type") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=format_error(ErrorCode.INVALID_TOKEN, "Invalid verification token")
            )

        user_id = UUID(payload["sub"])

        # Find and update user
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=format_error(ErrorCode.USER_NOT_FOUND, "User not found")
            )

        user.email_verified = True
        await session.commit()

        return MessageResponse(message="Email verified successfully")

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_error(ErrorCode.TOKEN_EXPIRED, "Verification link expired")
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_error(ErrorCode.INVALID_TOKEN, "Invalid verification token")
        )


# T041: POST /api/auth/signin
@router.post(
    "/signin",
    response_model=SigninResponse,
    responses={
        200: {"description": "Login successful", "model": SigninResponse},
        401: {"description": "Invalid credentials", "model": ErrorResponse},
        403: {"description": "Email not verified", "model": ErrorResponse},
        423: {"description": "Account locked due to too many failed attempts", "model": ErrorResponse},
    },
    summary="Sign in user",
    description="Authenticate with email and password. Returns JWT access (1h) and refresh (7d) tokens. "
                "Account locks after 5 failed attempts for 15 minutes.",
)
async def signin(
    request: SigninRequest,
    http_request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Sign in with email and password.

    Returns JWT access and refresh tokens on success.
    Implements account lockout after 5 failed attempts.
    """
    ip_address = get_client_ip(http_request)

    # Check if account is locked
    is_locked, minutes_remaining = check_account_lockout(request.email)
    if is_locked:
        log_signin_failed(request.email, "account_locked", ip_address)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=format_error(
                ErrorCode.ACCOUNT_LOCKED,
                f"Account locked due to too many failed attempts. Try again in {minutes_remaining} minutes."
            )
        )

    # Find user by email
    result = await session.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    # Return same error for non-existent user (security)
    if not user or not verify_password(request.password, user.password_hash):
        # Record failed attempt
        is_now_locked, lockout_minutes = record_failed_signin(request.email)

        if is_now_locked:
            log_account_locked(request.email, 5, lockout_minutes, ip_address)
            log_signin_failed(request.email, "invalid_credentials_locked", ip_address)
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=format_error(
                    ErrorCode.ACCOUNT_LOCKED,
                    f"Account locked due to too many failed attempts. Try again in {LOCKOUT_DURATION_MINUTES} minutes."
                )
            )

        log_signin_failed(request.email, "invalid_credentials", ip_address)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_error(ErrorCode.INVALID_CREDENTIALS, "Invalid email or password")
        )

    # Check email verification
    if not user.email_verified:
        log_signin_failed(request.email, "email_not_verified", ip_address)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=format_error(ErrorCode.EMAIL_NOT_VERIFIED, "Please verify your email before signing in")
        )

    # Clear failed attempts on successful signin
    record_successful_signin(request.email)

    # Update last signin timestamp
    user.last_signin_at = datetime.utcnow()
    await session.commit()

    # Generate tokens
    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id, user.email)

    # Audit log successful signin
    log_signin_success(str(user.id), user.email, ip_address)

    return SigninResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# T042: POST /api/auth/refresh
@router.post(
    "/refresh",
    response_model=SigninResponse,
    responses={
        200: {"description": "Tokens refreshed successfully", "model": SigninResponse},
        401: {"description": "Invalid or expired refresh token", "model": ErrorResponse},
    },
    summary="Refresh access token",
    description="Exchange a valid refresh token for new access and refresh tokens. "
                "Refresh token expires after 7 days.",
)
async def refresh_token(
    request: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Refresh access token using refresh token."""
    try:
        payload = jwt.decode(
            request.refresh_token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=format_error(ErrorCode.INVALID_TOKEN, "Invalid refresh token")
            )

        user_id = UUID(payload["sub"])
        email = payload["email"]

        # Verify user still exists
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=format_error(ErrorCode.INVALID_TOKEN, "User not found")
            )

        # Generate new tokens
        access_token = create_access_token(user.id, user.email)
        new_refresh_token = create_refresh_token(user.id, user.email)

        return SigninResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_error(ErrorCode.TOKEN_EXPIRED, "Refresh token expired. Please sign in again.")
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_error(ErrorCode.INVALID_TOKEN, "Invalid refresh token")
        )


# T043: POST /api/auth/signout
@router.post(
    "/signout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Signed out successfully"},
        401: {"description": "Invalid or missing authentication token", "model": ErrorResponse},
    },
    summary="Sign out user",
    description="Sign out the current user. Client should discard stored tokens.",
)
async def signout(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Sign out current user.

    Clears tokens (client should discard tokens).
    For full security, implement token blacklisting.
    """
    # Note: Stateless JWT - client should discard tokens
    # For enhanced security, implement token blacklisting here
    return None


# T044: POST /api/auth/reset-password-request
@router.post(
    "/reset-password-request",
    response_model=MessageResponse,
    responses={
        200: {"description": "Reset email sent if account exists", "model": MessageResponse},
    },
    summary="Request password reset",
    description="Request a password reset email. Always returns 200 to not reveal whether email exists. "
                "Reset link expires after 1 hour.",
)
async def request_password_reset(
    request: ResetPasswordRequestSchema,
    http_request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Request password reset email.

    Always returns 200 to not reveal email existence.
    """
    ip_address = get_client_ip(http_request)

    # Find user by email
    result = await session.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if user:
        # Generate reset token and send email
        reset_token = create_password_reset_token(user.id, user.email)
        # TODO: Send reset email via email service
        # await send_password_reset_email(user.email, reset_token)

    # Audit log the request (regardless of whether user exists)
    log_password_reset_request(request.email, ip_address)

    # Always return success to not reveal email existence
    return MessageResponse(message="If this email exists, a password reset link has been sent.")


# T045: POST /api/auth/reset-password
@router.post(
    "/reset-password",
    response_model=MessageResponse,
    responses={
        200: {"description": "Password reset successfully", "model": MessageResponse},
        401: {"description": "Invalid or expired reset token", "model": ErrorResponse},
        422: {"description": "Password validation error", "model": ErrorResponse},
    },
    summary="Reset password",
    description="Reset password using token from reset email. Token expires after 1 hour. "
                "New password must meet strength requirements.",
)
async def reset_password(
    request: ResetPasswordSchema,
    http_request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Reset password with valid token."""
    ip_address = get_client_ip(http_request)

    try:
        payload = jwt.decode(
            request.token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        if payload.get("token_type") != "password_reset":
            log_password_reset(user_id="unknown", ip_address=ip_address, success=False)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=format_error(ErrorCode.INVALID_TOKEN, "Invalid reset token")
            )

        user_id = UUID(payload["sub"])

        # Find and update user
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            log_password_reset(str(user_id), ip_address, success=False)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=format_error(ErrorCode.INVALID_TOKEN, "Invalid reset token")
            )

        # Update password
        user.password_hash = hash_password(request.new_password)
        await session.commit()

        # Audit log successful password reset
        log_password_reset(str(user.id), ip_address, success=True)

        return MessageResponse(message="Password reset successfully")

    except ExpiredSignatureError:
        log_password_reset(user_id="unknown", ip_address=ip_address, success=False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_error(ErrorCode.TOKEN_EXPIRED, "Reset link expired. Please request a new password reset.")
        )
    except InvalidTokenError:
        log_password_reset(user_id="unknown", ip_address=ip_address, success=False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_error(ErrorCode.INVALID_TOKEN, "Invalid reset token")
        )


# T046: GET /api/{user_id}/profile
@profile_router.get(
    "/api/{user_id}/profile",
    response_model=UserRead,
    responses={
        200: {"description": "Profile retrieved successfully", "model": UserRead},
        401: {"description": "Authentication required", "model": ErrorResponse},
        403: {"description": "Cannot access other users' profile", "model": ErrorResponse},
        404: {"description": "User not found", "model": ErrorResponse},
    },
    summary="Get user profile",
    description="Get the authenticated user's profile. User can only access their own profile.",
    tags=["profile"],
)
async def get_profile(
    user_id: str,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Get user profile.

    User can only access their own profile.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=format_error(ErrorCode.USER_NOT_FOUND, "User not found")
        )

    return UserRead.model_validate(user)


# T047: PUT /api/{user_id}/profile
@profile_router.put(
    "/api/{user_id}/profile",
    response_model=UserRead,
    responses={
        200: {"description": "Profile updated successfully", "model": UserRead},
        401: {"description": "Authentication required or invalid current password", "model": ErrorResponse},
        403: {"description": "Cannot update other users' profile", "model": ErrorResponse},
        404: {"description": "User not found", "model": ErrorResponse},
        422: {"description": "Validation error (password requirements)", "model": ErrorResponse},
    },
    summary="Update user profile",
    description="Update the authenticated user's profile. Password change requires current password.",
    tags=["profile"],
)
async def update_profile(
    user_id: str,
    request: ProfileUpdateRequest,
    http_request: Request,
    current_user: ValidatedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Update user profile.

    Can update display_name and password (requires current password).
    """
    ip_address = get_client_ip(http_request)

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=format_error(ErrorCode.USER_NOT_FOUND, "User not found")
        )

    # Update display name if provided
    if request.display_name is not None:
        user.display_name = request.display_name

    # Update password if provided
    if request.new_password is not None:
        if not request.current_password:
            log_password_change(str(user_id), ip_address, success=False)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=format_error(
                    ErrorCode.VALIDATION_ERROR,
                    "Current password required to change password",
                    "current_password"
                )
            )

        if not verify_password(request.current_password, user.password_hash):
            log_password_change(str(user_id), ip_address, success=False)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=format_error(ErrorCode.INVALID_CREDENTIALS, "Current password is incorrect")
            )

        user.password_hash = hash_password(request.new_password)

        # Audit log successful password change
        log_password_change(str(user.id), ip_address, success=True)

    await session.commit()
    await session.refresh(user)

    return UserRead.model_validate(user)
