"""Integration tests for task creation.

T059: [US2] Integration test for task creation
Tests valid task creation, validation errors, and authorization.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestTaskCreation:
    """Integration tests for POST /api/{user_id}/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_valid_task_returns_201(self, async_client: AsyncClient, authenticated_user):
        """Test that valid task creation returns 201 with task object."""
        user_id = authenticated_user["user_id"]
        auth_headers = authenticated_user["auth_headers"]

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json={
                "title": "Buy groceries",
                "description": "Get milk, eggs, bread",
                "priority": "High",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Get milk, eggs, bread"
        assert data["priority"] == "High"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_empty_title_returns_422(self, async_client: AsyncClient, authenticated_user):
        """Test that empty title returns 422 Unprocessable Entity."""
        user_id = authenticated_user["user_id"]
        auth_headers = authenticated_user["auth_headers"]

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json={
                "title": "",
                "description": "Some description",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert "title" in str(data).lower()

    @pytest.mark.asyncio
    async def test_title_over_200_chars_returns_422(self, async_client: AsyncClient, authenticated_user):
        """Test that title >200 characters returns 422."""
        user_id = authenticated_user["user_id"]
        auth_headers = authenticated_user["auth_headers"]

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json={
                "title": "a" * 201,
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_user_id_mismatch_returns_403(self, async_client: AsyncClient, authenticated_user, authenticated_other_user):
        """Test that user_id mismatch in URL returns 403 Forbidden."""
        # Use authenticated_user's token but try to access authenticated_other_user's endpoint
        other_user_id = authenticated_other_user["user_id"]
        auth_headers = authenticated_user["auth_headers"]

        response = await async_client.post(
            f"/api/{other_user_id}/tasks",
            json={
                "title": "Test Task",
            },
            headers=auth_headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["error_code"] == "FORBIDDEN"

    @pytest.mark.asyncio
    async def test_missing_auth_returns_401(self, async_client: AsyncClient, authenticated_user):
        """Test that missing authentication returns 401."""
        user_id = authenticated_user["user_id"]

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json={
                "title": "Test Task",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_description_truncated_at_2000_chars(self, async_client: AsyncClient, authenticated_user):
        """Test that description is truncated at 2000 characters."""
        user_id = authenticated_user["user_id"]
        auth_headers = authenticated_user["auth_headers"]

        long_description = "a" * 2500
        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json={
                "title": "Test Task",
                "description": long_description,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["description"]) == 2000

    @pytest.mark.asyncio
    async def test_default_priority_is_medium(self, async_client: AsyncClient, authenticated_user):
        """Test that default priority is medium when not specified."""
        user_id = authenticated_user["user_id"]
        auth_headers = authenticated_user["auth_headers"]

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json={
                "title": "Test Task",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "Medium"
