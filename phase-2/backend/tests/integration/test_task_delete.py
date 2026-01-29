"""Integration tests for task deletion.

T063: [US2] Integration test for task deletion
Tests valid deletion, cross-user access, and non-existent task.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestTaskDeletion:
    """Integration tests for DELETE /api/{user_id}/tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_valid_deletion_returns_204(self, async_client: AsyncClient, test_user_id):
        """Test that valid deletion returns 204 No Content."""
        # Create a task first
        create_response = await async_client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task to Delete"},
            headers={"Authorization": "Bearer valid_token"},
        )
        task_id = create_response.json()["id"]

        # Delete the task
        response = await async_client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 204

        # Verify task is deleted (should return 404)
        get_response = await async_client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"},
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_cross_user_deletion_returns_403(self, async_client: AsyncClient):
        """Test that cross-user deletion returns 403 Forbidden."""
        user_a_id = uuid4()
        user_b_id = uuid4()

        # Create task as user A
        create_response = await async_client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's Task"},
            headers={"Authorization": f"Bearer token_for_{user_a_id}"},
        )
        task_id = create_response.json()["id"]

        # User B tries to delete User A's task
        response = await async_client.delete(
            f"/api/{user_a_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer token_for_{user_b_id}"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_nonexistent_task_returns_404(self, async_client: AsyncClient, test_user_id):
        """Test that deleting nonexistent task returns 404."""
        fake_task_id = uuid4()

        response = await async_client.delete(
            f"/api/{test_user_id}/tasks/{fake_task_id}",
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_already_deleted_returns_404(
        self, async_client: AsyncClient, test_user_id
    ):
        """Test that deleting already deleted task returns 404."""
        # Create and delete a task
        create_response = await async_client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task to Delete"},
            headers={"Authorization": "Bearer valid_token"},
        )
        task_id = create_response.json()["id"]

        # First deletion
        await async_client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"},
        )

        # Second deletion should return 404
        response = await async_client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_removes_from_list(self, async_client: AsyncClient, test_user_id):
        """Test that deleted task is removed from task list."""
        # Create multiple tasks
        task_ids = []
        for i in range(3):
            create_response = await async_client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers={"Authorization": "Bearer valid_token"},
            )
            task_ids.append(create_response.json()["id"])

        # Delete the middle task
        await async_client.delete(
            f"/api/{test_user_id}/tasks/{task_ids[1]}",
            headers={"Authorization": "Bearer valid_token"},
        )

        # Get task list
        response = await async_client.get(
            f"/api/{test_user_id}/tasks",
            headers={"Authorization": "Bearer valid_token"},
        )

        assert response.status_code == 200
        data = response.json()
        remaining_ids = [task["id"] for task in data["tasks"]]

        assert task_ids[0] in remaining_ids
        assert task_ids[1] not in remaining_ids  # Deleted
        assert task_ids[2] in remaining_ids
