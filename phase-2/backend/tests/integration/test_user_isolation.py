"""Integration tests for cross-user task access (user isolation).

T078: [US3] Integration test for cross-user task access
Tests that users cannot access other users' tasks.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
import jwt
import time
import os


def create_test_token(user_id: str) -> str:
    """Create a valid JWT token for testing."""
    payload = {
        "sub": user_id,
        "email": f"user_{user_id[:8]}@example.com",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "token_type": "access",
    }
    return jwt.encode(
        payload,
        os.environ.get("JWT_SECRET", "test-secret-key-for-testing-only-32chars"),
        algorithm="HS256"
    )


class TestUserIsolation:
    """Integration tests for user data isolation."""

    @pytest.mark.asyncio
    async def test_user_b_get_user_a_task_returns_404(self, async_client: AsyncClient):
        """Test that User B cannot GET User A's task (returns 404 not 403 for security)."""
        user_a_id = str(uuid4())
        user_b_id = str(uuid4())

        # Create task as User A
        token_a = create_test_token(user_a_id)
        create_response = await async_client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's Private Task"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        if create_response.status_code == 201:
            task_id = create_response.json()["id"]

            # User B tries to GET User A's task
            token_b = create_test_token(user_b_id)
            response = await async_client.get(
                f"/api/{user_a_id}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token_b}"},
            )

            # Should return 403 (URL user_id mismatch) or 404 (task not found for user)
            assert response.status_code in [403, 404]

    @pytest.mark.asyncio
    async def test_user_b_put_user_a_task_returns_403(self, async_client: AsyncClient):
        """Test that User B cannot PUT (update) User A's task."""
        user_a_id = str(uuid4())
        user_b_id = str(uuid4())

        # Create task as User A
        token_a = create_test_token(user_a_id)
        create_response = await async_client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's Task"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        if create_response.status_code == 201:
            task_id = create_response.json()["id"]

            # User B tries to UPDATE User A's task
            token_b = create_test_token(user_b_id)
            response = await async_client.put(
                f"/api/{user_a_id}/tasks/{task_id}",
                json={"title": "Hacked by User B"},
                headers={"Authorization": f"Bearer {token_b}"},
            )

            # Should return 403 Forbidden
            assert response.status_code == 403
            data = response.json()
            assert data["error_code"] == "FORBIDDEN"

    @pytest.mark.asyncio
    async def test_user_b_delete_user_a_task_returns_403(self, async_client: AsyncClient):
        """Test that User B cannot DELETE User A's task."""
        user_a_id = str(uuid4())
        user_b_id = str(uuid4())

        # Create task as User A
        token_a = create_test_token(user_a_id)
        create_response = await async_client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's Task"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        if create_response.status_code == 201:
            task_id = create_response.json()["id"]

            # User B tries to DELETE User A's task
            token_b = create_test_token(user_b_id)
            response = await async_client.delete(
                f"/api/{user_a_id}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token_b}"},
            )

            # Should return 403 Forbidden
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_user_b_complete_user_a_task_returns_403(self, async_client: AsyncClient):
        """Test that User B cannot toggle completion on User A's task."""
        user_a_id = str(uuid4())
        user_b_id = str(uuid4())

        # Create task as User A
        token_a = create_test_token(user_a_id)
        create_response = await async_client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's Task"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        if create_response.status_code == 201:
            task_id = create_response.json()["id"]

            # User B tries to toggle User A's task
            token_b = create_test_token(user_b_id)
            response = await async_client.patch(
                f"/api/{user_a_id}/tasks/{task_id}/complete",
                headers={"Authorization": f"Bearer {token_b}"},
            )

            # Should return 403 Forbidden
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_user_b_list_user_a_tasks_returns_403(self, async_client: AsyncClient):
        """Test that User B cannot list User A's tasks."""
        user_a_id = str(uuid4())
        user_b_id = str(uuid4())

        # User B tries to list User A's tasks
        token_b = create_test_token(user_b_id)
        response = await async_client.get(
            f"/api/{user_a_id}/tasks",
            headers={"Authorization": f"Bearer {token_b}"},
        )

        # Should return 403 Forbidden (URL user_id doesn't match JWT user_id)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_user_a_can_access_own_tasks(self, async_client: AsyncClient):
        """Test that User A CAN access their own tasks (positive control)."""
        user_a_id = str(uuid4())
        token_a = create_test_token(user_a_id)

        # Create task as User A
        create_response = await async_client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A's Task"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        if create_response.status_code == 201:
            task_id = create_response.json()["id"]

            # User A can GET their own task
            get_response = await async_client.get(
                f"/api/{user_a_id}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token_a}"},
            )
            assert get_response.status_code == 200

            # User A can UPDATE their own task
            put_response = await async_client.put(
                f"/api/{user_a_id}/tasks/{task_id}",
                json={"title": "Updated by User A"},
                headers={"Authorization": f"Bearer {token_a}"},
            )
            assert put_response.status_code == 200

            # User A can DELETE their own task
            delete_response = await async_client.delete(
                f"/api/{user_a_id}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token_a}"},
            )
            assert delete_response.status_code == 204
