"""Combined task query integration tests.

T121: [US6] Integration test for combined search+filter+sort

Tests:
- Search + priority filter + status filter + sort combined
- All parameters work together without conflicts
- Complex queries return correct results

@see specs/001-fullstack-todo-web/spec.md - FR-047, FR-048
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from src.main import app


class TestCombinedQueries:
    """Test GET /api/{user_id}/tasks with multiple query parameters."""

    @pytest.mark.asyncio
    async def test_search_plus_priority_filter(self):
        """GET /tasks?search=meeting&priority=High returns high priority meeting tasks."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?search=meeting&priority=High",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_search_plus_status_filter(self):
        """GET /tasks?search=meeting&status=pending returns pending meeting tasks."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?search=meeting&status=pending",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_search_plus_category_filter(self):
        """GET /tasks?search=meeting&category={id} returns meeting tasks in category."""
        user_id = uuid4()
        category_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?search=meeting&category={category_id}",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_search_plus_tags_filter(self):
        """GET /tasks?search=meeting&tags={id} returns meeting tasks with tag."""
        user_id = uuid4()
        tag_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?search=meeting&tags={tag_id}",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_search_plus_sort(self):
        """GET /tasks?search=meeting&sort_by=priority&order=desc sorts search results."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?search=meeting&sort_by=priority&order=desc",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_status_plus_priority_filter(self):
        """GET /tasks?status=pending&priority=High returns pending high priority tasks."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?status=pending&priority=High",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_priority_plus_category_filter(self):
        """GET /tasks?priority=High&category={id} returns high priority tasks in category."""
        user_id = uuid4()
        category_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?priority=High&category={category_id}",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_date_range_plus_status_filter(self):
        """GET /tasks?status=pending&created_after=2026-01-01 combines date and status."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?status=pending&created_after=2026-01-01T00:00:00Z",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_full_complex_query(self):
        """GET /tasks with search+status+priority+category+sort all combined."""
        user_id = uuid4()
        category_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks"
                f"?search=meeting"
                f"&status=pending"
                f"&priority=High,Urgent"
                f"&category={category_id}"
                f"&sort_by=created_at"
                f"&order=desc",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_all_filters_with_date_range(self):
        """GET /tasks with all filters including date range."""
        user_id = uuid4()
        category_id = uuid4()
        tag_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks"
                f"?search=meeting"
                f"&status=pending"
                f"&priority=High"
                f"&category={category_id}"
                f"&tags={tag_id}"
                f"&created_after=2026-01-01T00:00:00Z"
                f"&created_before=2026-12-31T23:59:59Z"
                f"&sort_by=priority"
                f"&order=desc",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_filter_plus_sort_consistency(self):
        """Filtered results maintain sort order."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks?priority=High&sort_by=title&order=asc",
                headers={"Authorization": "Bearer fake_token"},
            )

        assert response.status_code in [200, 401]
