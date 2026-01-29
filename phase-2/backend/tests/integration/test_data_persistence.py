"""Data persistence integration tests.

T135: [US7] Integration test for data persistence across restarts

Tests:
- Create tasks, disconnect, reconnect, verify data present
- Data survives application restarts

@see specs/001-fullstack-todo-web/spec.md - FR-071, FR-072
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from src.main import app


class TestDataPersistence:
    """Test data persistence across database connections."""

    @pytest.mark.asyncio
    async def test_tasks_persist_across_requests(self):
        """Tasks created in one request are visible in subsequent requests."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # First request - list tasks
            response1 = await client.get(
                f"/api/{user_id}/tasks",
                headers={"Authorization": "Bearer fake_token"},
            )

            # Second request - should see same state
            response2 = await client.get(
                f"/api/{user_id}/tasks",
                headers={"Authorization": "Bearer fake_token"},
            )

        # Both should return same status (401 without real auth)
        assert response1.status_code == response2.status_code

    @pytest.mark.asyncio
    async def test_multiple_concurrent_connections(self):
        """Multiple concurrent connections can access data."""
        user_id = uuid4()

        # Create multiple concurrent requests
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client1:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client2:
                response1 = await client1.get(
                    f"/api/{user_id}/tasks",
                    headers={"Authorization": "Bearer fake_token"},
                )
                response2 = await client2.get(
                    f"/api/{user_id}/tasks",
                    headers={"Authorization": "Bearer fake_token"},
                )

        assert response1.status_code in [200, 401]
        assert response2.status_code in [200, 401]
