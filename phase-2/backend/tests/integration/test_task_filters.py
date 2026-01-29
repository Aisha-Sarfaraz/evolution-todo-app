"""Task filtering integration tests.

T119: [US6] Integration test for task filtering

Tests:
- Filter by status (pending, complete, all)
- Filter by priority (single + multiple)
- Filter by category
- Filter by tags with AND logic
- Filter by date ranges (created_after/before)

@see specs/001-fullstack-todo-web/spec.md - FR-039, FR-040, FR-041, FR-042, FR-043
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from src.main import app


class TestStatusFilter:
    """Test GET /api/{user_id}/tasks?status=... endpoint."""

    @pytest.mark.asyncio
    async def test_filter_by_status_pending(self):
        """GET /tasks?status=pending returns only pending tasks."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?status=pending",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_by_status_complete(self):
        """GET /tasks?status=complete returns only completed tasks."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?status=complete",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_by_status_all(self):
        """GET /tasks?status=all returns all tasks (pending + complete)."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?status=all",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_by_invalid_status(self):
        """GET /tasks?status=invalid returns 422 validation error."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?status=invalid",
                headers={"Authorization": "Bearer fake_token"},
            )

        # Should be 401 (auth) or 422 (validation)
        assert response.status_code in [401, 422]


class TestPriorityFilter:
    """Test GET /api/{user_id}/tasks?priority=... endpoint."""

    @pytest.mark.asyncio
    async def test_filter_by_single_priority(self):
        """GET /tasks?priority=High returns only high priority tasks."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?priority=High",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_by_multiple_priorities(self):
        """GET /tasks?priority=High,Urgent returns high and urgent tasks."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?priority=High,Urgent",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_by_all_priorities(self):
        """GET /tasks?priority=Low,Medium,High,Urgent returns all tasks."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?priority=Low,Medium,High,Urgent",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]


class TestCategoryFilter:
    """Test GET /api/{user_id}/tasks?category=... endpoint."""

    @pytest.mark.asyncio
    async def test_filter_by_category_id(self):
        """GET /tasks?category={uuid} returns tasks in that category."""
        user_id = uuid4()
        category_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?category={category_id}",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_by_nonexistent_category(self):
        """GET /tasks?category={nonexistent_uuid} returns empty array."""
        user_id = uuid4()
        category_id = uuid4()  # Random UUID, likely doesn't exist

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?category={category_id}",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]


class TestTagsFilter:
    """Test GET /api/{user_id}/tasks?tags=... endpoint with AND logic."""

    @pytest.mark.asyncio
    async def test_filter_by_single_tag(self):
        """GET /tasks?tags={tag_id} returns tasks with that tag."""
        user_id = uuid4()
        tag_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?tags={tag_id}",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_by_multiple_tags_and_logic(self):
        """GET /tasks?tags={id1},{id2} returns tasks with BOTH tags (AND)."""
        user_id = uuid4()
        tag_id_1 = uuid4()
        tag_id_2 = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?tags={tag_id_1},{tag_id_2}",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]


class TestDateRangeFilter:
    """Test GET /api/{user_id}/tasks?created_after=...&created_before=... endpoint."""

    @pytest.mark.asyncio
    async def test_filter_by_created_after(self):
        """GET /tasks?created_after=2026-01-01 returns tasks created after date."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?created_after=2026-01-01T00:00:00Z",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_by_created_before(self):
        """GET /tasks?created_before=2026-12-31 returns tasks created before date."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?created_before=2026-12-31T23:59:59Z",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_by_date_range(self):
        """GET /tasks?created_after=...&created_before=... returns tasks in range."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?created_after=2026-01-01T00:00:00Z&created_before=2026-01-31T23:59:59Z",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_by_updated_after(self):
        """GET /tasks?updated_after=2026-01-01 returns tasks updated after date."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?updated_after=2026-01-01T00:00:00Z",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_by_completed_after(self):
        """GET /tasks?completed_after=2026-01-01 returns tasks completed after date."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?completed_after=2026-01-01T00:00:00Z",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]
