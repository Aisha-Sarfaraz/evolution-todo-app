"""Integration tests for task update.

T061: [US2] Integration test for task update
Tests valid updates, cross-user access, and validation.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestTaskUpdate:
    """Integration tests for PUT /api/{user_id}/tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_valid_update_returns_200(self, async_client: AsyncClient, test_user_id):
        """Test that valid update returns 200 with updated task."""
        # Create a task first
        create_response = await async_client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original Title", "description": "Original description"},
            headers={"Authorization": "Bearer valid_token"},
        )
        task_id = create_response.json()["id"]

        # Update the task
        response = await async_client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"title": "Updated Title", "description": "Updated description"},
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_cross_user_update_returns_403(self, async_client: AsyncClient):
        """Test that cross-user update returns 403 Forbidden."""
        user_a_id = uuid4()
        user_b_id = uuid4()

        # Create task as user A
        create_response = await async_client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's Task"},
            headers={"Authorization": f"Bearer token_for_{user_a_id}"},
        )
        task_id = create_response.json()["id"]

        # User B tries to update User A's task
        response = await async_client.put(
            f"/api/{user_a_id}/tasks/{task_id}",
            json={"title": "Hacked Title"},
            headers={"Authorization": f"Bearer token_for_{user_b_id}"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_empty_title_returns_422(self, async_client: AsyncClient, test_user_id):
        """Test that empty title returns 422."""
        # Create a task first
        create_response = await async_client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original Title"},
            headers={"Authorization": "Bearer valid_token"},
        )
        task_id = create_response.json()["id"]

        # Try to update with empty title
        response = await async_client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"title": ""},
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_nonexistent_task_returns_404(self, async_client: AsyncClient, test_user_id):
        """Test that updating nonexistent task returns 404."""
        fake_task_id = uuid4()

        response = await async_client.put(
            f"/api/{test_user_id}/tasks/{fake_task_id}",
            json={"title": "Updated Title"},
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_partial_update_preserves_other_fields(self, async_client: AsyncClient, test_user_id):
        """Test that partial update preserves unchanged fields."""
        # Create a task with all fields
        create_response = await async_client.post(
            f"/api/{test_user_id}/tasks",
            json={
                "title": "Original Title",
                "description": "Original description",
                "priority": "high",
            },
            headers={"Authorization": "Bearer valid_token"},
        )
        task_id = create_response.json()["id"]

        # Update only the title
        response = await async_client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"title": "New Title"},
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "Original description"  # Preserved
        assert data["priority"] == "high"  # Preserved

    @pytest.mark.asyncio
    async def test_update_sets_updated_at(self, async_client: AsyncClient, test_user_id):
        """Test that update sets updated_at timestamp."""
        # Create a task
        create_response = await async_client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original Title"},
            headers={"Authorization": "Bearer valid_token"},
        )
        task = create_response.json()
        task_id = task["id"]
        original_updated_at = task.get("updated_at")

        # Update the task
        response = await async_client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"title": "Updated Title"},
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["updated_at"] is not None
        if original_updated_at:
            assert data["updated_at"] > original_updated_at
