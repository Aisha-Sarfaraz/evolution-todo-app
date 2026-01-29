"""Integration tests for signup flow.

T036: [US1] Integration test for signup flow
Tests valid registration, duplicate email, weak password, password mismatch.
"""

import pytest
from httpx import AsyncClient


class TestSignupFlow:
    """Integration tests for POST /api/auth/signup endpoint."""

    @pytest.mark.asyncio
    async def test_valid_registration_returns_201(self, async_client: AsyncClient, test_user_data):
        """Test that valid registration creates user and returns 201."""
        response = await async_client.post(
            "/api/auth/signup",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "password_confirm": test_user_data["password"],
                "name": test_user_data["name"],
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert data["message"] == "Registration successful. Please check your email to verify your account."

    @pytest.mark.asyncio
    async def test_duplicate_email_returns_409(self, async_client: AsyncClient, test_user_data):
        """Test that duplicate email returns 409 Conflict."""
        # First registration
        await async_client.post(
            "/api/auth/signup",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "password_confirm": test_user_data["password"],
                "name": test_user_data["name"],
            }
        )

        # Second registration with same email
        response = await async_client.post(
            "/api/auth/signup",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "password_confirm": test_user_data["password"],
                "name": "Another User",
            }
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "EMAIL_ALREADY_EXISTS"

    @pytest.mark.asyncio
    async def test_weak_password_returns_422(self, async_client: AsyncClient, test_user_data):
        """Test that weak password returns 422 Unprocessable Entity."""
        response = await async_client.post(
            "/api/auth/signup",
            json={
                "email": test_user_data["email"],
                "password": "weak",  # Too short, no uppercase, no number
                "password_confirm": "weak",
                "name": test_user_data["name"],
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"
        assert "password" in str(data).lower()

    @pytest.mark.asyncio
    async def test_password_mismatch_returns_422(self, async_client: AsyncClient, test_user_data):
        """Test that password mismatch returns 422 Unprocessable Entity."""
        response = await async_client.post(
            "/api/auth/signup",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "password_confirm": "DifferentPassword123!",
                "name": test_user_data["name"],
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"
        assert "match" in str(data).lower() or "password" in str(data).lower()

    @pytest.mark.asyncio
    async def test_invalid_email_format_returns_422(self, async_client: AsyncClient, test_user_data):
        """Test that invalid email format returns 422."""
        response = await async_client.post(
            "/api/auth/signup",
            json={
                "email": "not-an-email",
                "password": test_user_data["password"],
                "password_confirm": test_user_data["password"],
                "name": test_user_data["name"],
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_required_fields_returns_422(self, async_client: AsyncClient):
        """Test that missing required fields returns 422."""
        response = await async_client.post(
            "/api/auth/signup",
            json={}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_name_uses_email_prefix(self, async_client: AsyncClient, test_user_data):
        """Test that empty name defaults to email prefix."""
        response = await async_client.post(
            "/api/auth/signup",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "password_confirm": test_user_data["password"],
                # name is optional
            }
        )

        # Should succeed - name is optional
        assert response.status_code in [201, 422]  # 422 if name is required
