"""Integration tests for task list.

T060: [US2] Integration test for task list
Tests user isolation and empty list handling.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from tests.conftest import create_test_jwt


class TestTaskList:
    """Integration tests for GET /api/{user_id}/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_user_a_sees_only_user_a_tasks(self, async_client: AsyncClient):
        """Test that user A only sees their own tasks."""
        user_a_id = str(uuid4())
        user_b_id = str(uuid4())
        token_a = create_test_jwt(user_a_id)
        token_b = create_test_jwt(user_b_id)

        # Create task for user A
        await async_client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A Task"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        # Create task for user B
        await async_client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "User B Task"},
            headers={"Authorization": f"Bearer {token_b}"},
        )

        # User A should only see their task
        response = await async_client.get(
            f"/api/{user_a_id}/tasks",
            headers={"Authorization": f"Bearer {token_a}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert all(task["user_id"] == user_a_id for task in data["tasks"])

    @pytest.mark.asyncio
    async def test_user_b_sees_only_user_b_tasks(self, async_client: AsyncClient):
        """Test that user B only sees their own tasks."""
        user_a_id = str(uuid4())
        user_b_id = str(uuid4())
        token_a = create_test_jwt(user_a_id)
        token_b = create_test_jwt(user_b_id)

        # Create tasks for both users
        await async_client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A Task"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        await async_client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "User B Task"},
            headers={"Authorization": f"Bearer {token_b}"},
        )

        # User B should only see their task
        response = await async_client.get(
            f"/api/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {token_b}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert all(task["user_id"] == user_b_id for task in data["tasks"])

    @pytest.mark.asyncio
    async def test_empty_list_returns_empty_array(self, async_client: AsyncClient, test_user_id, auth_headers):
        """Test that user with no tasks gets empty array."""
        response = await async_client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_tasks_sorted_by_created_at_desc(self, async_client: AsyncClient, test_user_id, auth_headers):
        """Test that tasks are sorted by created_at DESC by default."""
        # Create multiple tasks
        for i in range(3):
            await async_client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        response = await async_client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        tasks = data["tasks"]

        # Verify descending order (newest first)
        for i in range(len(tasks) - 1):
            assert tasks[i]["created_at"] >= tasks[i + 1]["created_at"]

    @pytest.mark.asyncio
    async def test_cross_user_list_returns_403(self, async_client: AsyncClient):
        """Test that accessing another user's task list returns 403."""
        user_a_id = str(uuid4())
        user_b_id = str(uuid4())
        token_a = create_test_jwt(user_a_id)

        # User A tries to access User B's tasks
        response = await async_client.get(
            f"/api/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {token_a}"},
        )

        assert response.status_code == 403
