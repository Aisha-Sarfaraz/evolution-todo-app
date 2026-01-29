"""FastAPI dependencies for authentication and authorization.

T023-T024: JWT validation and user ID matching dependencies.
T087: Add audit logging for cross-user access attempts.

Updated to use Better Auth JWKS for JWT verification.
Uses PyJWT (with cryptography) for EdDSA/Ed25519 support.
"""

from typing import Annotated
import os
import time
import httpx

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import PyJWK, PyJWKSet
from pydantic import BaseModel

from src.utils.logging import log_unauthorized_access, log_forbidden_access


# Better Auth configuration from environment
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
BETTER_AUTH_ISSUER = os.getenv("BETTER_AUTH_ISSUER", BETTER_AUTH_URL)
BETTER_AUTH_AUDIENCE = os.getenv("BETTER_AUTH_AUDIENCE", BETTER_AUTH_URL)

# JWKS cache configuration
JWKS_CACHE_TTL = int(os.getenv("JWKS_CACHE_TTL", "300"))  # 5 minutes default

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


class TokenPayload(BaseModel):
    """JWT token payload model."""
    sub: str
    email: str | None = None
    iat: int | None = None
    exp: int | None = None


class CurrentUser(BaseModel):
    """Authenticated user context extracted from JWT."""
    user_id: str
    email: str | None = None


# JWKS cache with timestamp
_jwks_cache: dict | None = None
_jwks_cache_time: float = 0


async def fetch_jwks() -> dict:
    """Fetch JWKS from Better Auth server.

    Keys are cached for JWKS_CACHE_TTL seconds to reduce network overhead.
    """
    global _jwks_cache, _jwks_cache_time

    current_time = time.time()

    # Return cached JWKS if still valid
    if _jwks_cache and (current_time - _jwks_cache_time) < JWKS_CACHE_TTL:
        return _jwks_cache

    jwks_url = f"{BETTER_AUTH_URL}/api/auth/jwks"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            _jwks_cache = response.json()
            _jwks_cache_time = current_time
            return _jwks_cache
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "AUTH_SERVICE_UNAVAILABLE",
                "detail": f"Unable to fetch authentication keys: {str(e)}"
            }
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "AUTH_SERVICE_ERROR",
                "detail": f"Authentication service error: {e.response.status_code}"
            }
        )


def get_signing_key(jwks: dict, token: str) -> PyJWK:
    """Extract the correct signing key from JWKS based on token's kid.

    Returns a PyJWK object for use with PyJWT's decode.
    """
    try:
        # Decode header without verification to get kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            # If no kid, use the first key
            if jwks.get("keys"):
                return PyJWK(jwks["keys"][0])
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error_code": "INVALID_TOKEN",
                    "detail": "No signing key available"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Find matching key by kid
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return PyJWK(key)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_TOKEN",
                "detail": "Token signing key not found"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_TOKEN",
                "detail": "Malformed token header"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
) -> CurrentUser:
    """Dependency for extracting and validating JWT token.

    Decodes the JWT token from Authorization header using Better Auth's JWKS,
    validates signature, checks expiration, and returns user context.
    """
    # Check if credentials provided
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "AUTHENTICATION_REQUIRED",
                "detail": "Valid authentication token required"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Fetch JWKS from Better Auth
        jwks = await fetch_jwks()

        # Get the correct signing key as PyJWK
        signing_key = get_signing_key(jwks, token)

        # Decode and validate JWT token
        # Better Auth uses EdDSA (Ed25519) by default
        allowed_algorithms = os.getenv(
            "ALLOWED_JWT_ALGORITHMS", "EdDSA,RS256,ES256"
        ).split(",")

        # Decode JWT - disable aud/iss verification since Better Auth
        # may not include these claims in all configurations
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=allowed_algorithms,
            options={
                "verify_aud": False,
                "verify_iss": False,
            }
        )

        # Extract user_id from sub claim
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error_code": "INVALID_TOKEN",
                    "detail": "Token missing subject claim"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        return CurrentUser(
            user_id=str(user_id),
            email=payload.get("email")
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "TOKEN_EXPIRED",
                "detail": "Token has expired. Please refresh or sign in again."
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_TOKEN",
                "detail": f"Authentication token is invalid: {str(e)}"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def validate_user_id_match(
    user_id: str,
    request: Request,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> CurrentUser:
    """Dependency for validating URL user_id matches JWT user_id."""
    if user_id != current_user.user_id:
        # Extract IP address for audit logging
        forwarded_for = request.headers.get("X-Forwarded-For")
        ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else (
            request.client.host if request.client else "unknown"
        )

        # Audit log the cross-user access attempt
        log_forbidden_access(
            user_id=str(current_user.user_id),
            resource_owner_id=str(user_id),
            resource_type="user_resource",
            resource_id=str(user_id),
            action=request.method,
            ip_address=ip_address,
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "FORBIDDEN",
                "detail": "Cannot access other users' resources"
            }
        )

    return current_user


# Type aliases for dependency injection
GetCurrentUser = Annotated[CurrentUser, Depends(get_current_user)]
ValidatedUser = Annotated[CurrentUser, Depends(validate_user_id_match)]
