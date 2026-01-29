"""Integration tests for task completion.

T062: [US2] Integration test for task completion
Tests toggle status and completed_at timestamp handling.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestTaskCompletion:
    """Integration tests for PATCH /api/{user_id}/tasks/{id}/complete endpoint."""

    @pytest.mark.asyncio
    async def test_toggle_pending_to_complete_sets_completed_at(
        self, async_client: AsyncClient, test_user_id
    ):
        """Test that toggling pending→complete sets completed_at timestamp."""
        # Create a pending task
        create_response = await async_client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test Task"},
            headers={"Authorization": "Bearer valid_token"},
        )
        task_id = create_response.json()["id"]

        # Toggle to complete
        response = await async_client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_toggle_complete_to_pending_clears_completed_at(
        self, async_client: AsyncClient, test_user_id
    ):
        """Test that toggling complete→pending clears completed_at."""
        # Create and complete a task
        create_response = await async_client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test Task"},
            headers={"Authorization": "Bearer valid_token"},
        )
        task_id = create_response.json()["id"]

        # Complete the task
        await async_client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token"},
        )

        # Toggle back to pending
        response = await async_client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["completed_at"] is None

    @pytest.mark.asyncio
    async def test_cross_user_toggle_returns_403(self, async_client: AsyncClient):
        """Test that cross-user toggle returns 403 Forbidden."""
        user_a_id = uuid4()
        user_b_id = uuid4()

        # Create task as user A
        create_response = await async_client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's Task"},
            headers={"Authorization": f"Bearer token_for_{user_a_id}"},
        )
        task_id = create_response.json()["id"]

        # User B tries to toggle User A's task
        response = await async_client.patch(
            f"/api/{user_a_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer token_for_{user_b_id}"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_nonexistent_task_returns_404(self, async_client: AsyncClient, test_user_id):
        """Test that toggling nonexistent task returns 404."""
        fake_task_id = uuid4()

        response = await async_client.patch(
            f"/api/{test_user_id}/tasks/{fake_task_id}/complete",
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_multiple_toggles_work_correctly(
        self, async_client: AsyncClient, test_user_id
    ):
        """Test that multiple toggles work correctly."""
        # Create a pending task
        create_response = await async_client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test Task"},
            headers={"Authorization": "Bearer valid_token"},
        )
        task_id = create_response.json()["id"]

        # Toggle 1: pending → completed
        response1 = await async_client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token"},
        )
        assert response1.json()["status"] == "completed"

        # Toggle 2: completed → pending
        response2 = await async_client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token"},
        )
        assert response2.json()["status"] == "pending"

        # Toggle 3: pending → completed
        response3 = await async_client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token"},
        )
        assert response3.json()["status"] == "completed"
