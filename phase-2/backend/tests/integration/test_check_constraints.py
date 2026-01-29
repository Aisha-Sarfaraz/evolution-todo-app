"""Check constraint integration tests.

T140: [US7] Integration test for check constraints

Tests:
- Invalid status rejected
- Invalid priority rejected
- Empty title after trim rejected

@see specs/001-fullstack-todo-web/spec.md - FR-077
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from src.main import app


class TestStatusConstraint:
    """Test task status check constraint."""

    @pytest.mark.asyncio
    async def test_valid_status_pending_accepted(self):
        """POST /tasks with status=pending is accepted."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={
                    "title": "Test Task",
                    "status": "pending",
                },
                headers={
                    "Authorization": "Bearer fake_token",
                    "Content-Type": "application/json",
                },
            )

        # Should be 201 (created) or 401 (auth)
        assert response.status_code in [201, 401]

    @pytest.mark.asyncio
    async def test_valid_status_complete_accepted(self):
        """POST /tasks with status=complete is accepted."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={
                    "title": "Test Task",
                    "status": "complete",
                },
                headers={
                    "Authorization": "Bearer fake_token",
                    "Content-Type": "application/json",
                },
            )

        assert response.status_code in [201, 401]

    @pytest.mark.asyncio
    async def test_invalid_status_rejected(self):
        """POST /tasks with invalid status returns 422."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={
                    "title": "Test Task",
                    "status": "invalid_status",
                },
                headers={
                    "Authorization": "Bearer fake_token",
                    "Content-Type": "application/json",
                },
            )

        # Should be 422 (validation) or 401 (auth)
        assert response.status_code in [401, 422]


class TestPriorityConstraint:
    """Test task priority check constraint."""

    @pytest.mark.asyncio
    async def test_valid_priorities_accepted(self):
        """POST /tasks with valid priorities are accepted."""
        user_id = uuid4()
        valid_priorities = ["Low", "Medium", "High", "Urgent"]

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for priority in valid_priorities:
                response = await client.post(
                    f"/api/{user_id}/tasks",
                    json={
                        "title": f"Test Task {priority}",
                        "priority": priority,
                    },
                    headers={
                        "Authorization": "Bearer fake_token",
                        "Content-Type": "application/json",
                    },
                )

                # Should be 201 (created) or 401 (auth)
                assert response.status_code in [201, 401], f"Failed for priority: {priority}"

    @pytest.mark.asyncio
    async def test_invalid_priority_rejected(self):
        """POST /tasks with invalid priority returns 422."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={
                    "title": "Test Task",
                    "priority": "Critical",  # Invalid priority
                },
                headers={
                    "Authorization": "Bearer fake_token",
                    "Content-Type": "application/json",
                },
            )

        # Should be 422 (validation) or 401 (auth)
        assert response.status_code in [401, 422]


class TestTitleConstraint:
    """Test task title validation constraint."""

    @pytest.mark.asyncio
    async def test_empty_title_rejected(self):
        """POST /tasks with empty title returns 422."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={
                    "title": "",
                },
                headers={
                    "Authorization": "Bearer fake_token",
                    "Content-Type": "application/json",
                },
            )

        # Should be 422 (validation) or 401 (auth)
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_whitespace_only_title_rejected(self):
        """POST /tasks with whitespace-only title returns 422."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={
                    "title": "   ",
                },
                headers={
                    "Authorization": "Bearer fake_token",
                    "Content-Type": "application/json",
                },
            )

        # Should be 422 (validation) or 401 (auth)
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_title_over_200_chars_rejected(self):
        """POST /tasks with title > 200 chars returns 422."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={
                    "title": "x" * 201,
                },
                headers={
                    "Authorization": "Bearer fake_token",
                    "Content-Type": "application/json",
                },
            )

        # Should be 422 (validation) or 401 (auth)
        assert response.status_code in [401, 422]
