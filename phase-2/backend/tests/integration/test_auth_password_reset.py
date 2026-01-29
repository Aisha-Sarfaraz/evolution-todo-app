"""Integration tests for password reset flow.

T038: [US1] Integration test for password reset
Tests request reset sends email, valid reset token, expired token.
"""

import pytest
import jwt
import time
import os
from httpx import AsyncClient


class TestPasswordResetFlow:
    """Integration tests for password reset endpoints."""

    @pytest.mark.asyncio
    async def test_request_reset_returns_200_for_existing_email(
        self, async_client: AsyncClient, test_user_data
    ):
        """Test that password reset request returns 200 for existing email."""
        # Create user first
        await async_client.post(
            "/api/auth/signup",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "password_confirm": test_user_data["password"],
                "name": test_user_data["name"],
            }
        )

        # Request password reset
        response = await async_client.post(
            "/api/auth/reset-password-request",
            json={
                "email": test_user_data["email"],
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "email" in data["message"].lower() or "sent" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_request_reset_returns_200_for_nonexistent_email(
        self, async_client: AsyncClient
    ):
        """Test that password reset request returns 200 even for nonexistent email.

        This is a security measure to not reveal whether an email exists.
        """
        response = await async_client.post(
            "/api/auth/reset-password-request",
            json={
                "email": "nonexistent@example.com",
            }
        )

        # Return 200 to not reveal email existence
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_valid_reset_token_updates_password(
        self, async_client: AsyncClient, test_user_data
    ):
        """Test that valid reset token allows password update."""
        # Create user
        signup_response = await async_client.post(
            "/api/auth/signup",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "password_confirm": test_user_data["password"],
                "name": test_user_data["name"],
            }
        )
        user_id = signup_response.json().get("user_id")

        # Generate valid reset token (normally sent via email)
        reset_token = jwt.encode(
            {
                "sub": user_id,
                "email": test_user_data["email"],
                "iat": int(time.time()),
                "exp": int(time.time()) + 3600,  # 1 hour
                "token_type": "password_reset",
            },
            os.environ.get("JWT_SECRET", "test-secret-key-for-testing-only-32chars"),
            algorithm="HS256"
        )

        # Reset password
        new_password = "NewSecurePass456!"
        response = await async_client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": new_password,
                "new_password_confirm": new_password,
            }
        )

        assert response.status_code == 200

        # Verify can signin with new password
        signin_response = await async_client.post(
            "/api/auth/signin",
            json={
                "email": test_user_data["email"],
                "password": new_password,
            }
        )

        # Should succeed with new password (if email verified)
        assert signin_response.status_code in [200, 403]

    @pytest.mark.asyncio
    async def test_expired_reset_token_returns_401(
        self, async_client: AsyncClient, test_user_data
    ):
        """Test that expired reset token returns 401 Unauthorized."""
        # Create user
        signup_response = await async_client.post(
            "/api/auth/signup",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "password_confirm": test_user_data["password"],
                "name": test_user_data["name"],
            }
        )
        user_id = signup_response.json().get("user_id")

        # Generate expired reset token
        expired_token = jwt.encode(
            {
                "sub": user_id,
                "email": test_user_data["email"],
                "iat": int(time.time()) - 7200,  # 2 hours ago
                "exp": int(time.time()) - 3600,  # Expired 1 hour ago
                "token_type": "password_reset",
            },
            os.environ.get("JWT_SECRET", "test-secret-key-for-testing-only-32chars"),
            algorithm="HS256"
        )

        # Attempt reset with expired token
        response = await async_client.post(
            "/api/auth/reset-password",
            json={
                "token": expired_token,
                "new_password": "NewSecurePass456!",
                "new_password_confirm": "NewSecurePass456!",
            }
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error_code"] == "TOKEN_EXPIRED"

    @pytest.mark.asyncio
    async def test_invalid_reset_token_returns_401(self, async_client: AsyncClient):
        """Test that invalid reset token returns 401."""
        response = await async_client.post(
            "/api/auth/reset-password",
            json={
                "token": "invalid.token.here",
                "new_password": "NewSecurePass456!",
                "new_password_confirm": "NewSecurePass456!",
            }
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error_code"] == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_password_mismatch_in_reset_returns_422(
        self, async_client: AsyncClient, test_user_data
    ):
        """Test that password mismatch in reset returns 422."""
        # Create user and get valid token
        signup_response = await async_client.post(
            "/api/auth/signup",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "password_confirm": test_user_data["password"],
                "name": test_user_data["name"],
            }
        )
        user_id = signup_response.json().get("user_id")

        reset_token = jwt.encode(
            {
                "sub": user_id,
                "email": test_user_data["email"],
                "iat": int(time.time()),
                "exp": int(time.time()) + 3600,
                "token_type": "password_reset",
            },
            os.environ.get("JWT_SECRET", "test-secret-key-for-testing-only-32chars"),
            algorithm="HS256"
        )

        # Attempt reset with mismatched passwords
        response = await async_client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewSecurePass456!",
                "new_password_confirm": "DifferentPass789!",
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_weak_new_password_returns_422(
        self, async_client: AsyncClient, test_user_data
    ):
        """Test that weak new password returns 422."""
        # Create user and get valid token
        signup_response = await async_client.post(
            "/api/auth/signup",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "password_confirm": test_user_data["password"],
                "name": test_user_data["name"],
            }
        )
        user_id = signup_response.json().get("user_id")

        reset_token = jwt.encode(
            {
                "sub": user_id,
                "email": test_user_data["email"],
                "iat": int(time.time()),
                "exp": int(time.time()) + 3600,
                "token_type": "password_reset",
            },
            os.environ.get("JWT_SECRET", "test-secret-key-for-testing-only-32chars"),
            algorithm="HS256"
        )

        # Attempt reset with weak password
        response = await async_client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "weak",
                "new_password_confirm": "weak",
            }
        )

        assert response.status_code == 422
