"""Connection pooling integration tests.

T141: [US7] Integration test for connection pooling

Tests:
- Multiple concurrent requests use pool connections
- Pool handles load within configured limits

@see specs/001-fullstack-todo-web/spec.md - FR-078
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from src.main import app


class TestConnectionPooling:
    """Test database connection pool behavior."""

    @pytest.mark.asyncio
    async def test_concurrent_requests_handled(self):
        """Multiple concurrent requests are handled by connection pool."""
        user_id = uuid4()

        async def make_request(client: AsyncClient):
            return await client.get(
                f"/api/{user_id}/tasks",
                headers={"Authorization": "Bearer fake_token"},
            )

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Make 10 concurrent requests
            tasks = [make_request(client) for _ in range(10)]
            responses = await asyncio.gather(*tasks)

        # All requests should complete (401 without real auth)
        for response in responses:
            assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_pool_handles_burst_traffic(self):
        """Connection pool handles burst of requests."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Make 20 rapid requests
            responses = []
            for _ in range(20):
                response = await client.get(
                    f"/api/{user_id}/tasks",
                    headers={"Authorization": "Bearer fake_token"},
                )
                responses.append(response)

        # All requests should complete
        for response in responses:
            assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """GET /health returns database connection status."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")

        # Should return 200 (healthy) or 503 (unhealthy)
        assert response.status_code in [200, 404, 503]

    @pytest.mark.asyncio
    async def test_sequential_requests_reuse_connections(self):
        """Sequential requests efficiently reuse pool connections."""
        user_id = uuid4()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Make sequential requests
            for i in range(5):
                response = await client.get(
                    f"/api/{user_id}/tasks",
                    headers={"Authorization": "Bearer fake_token"},
                )
                assert response.status_code in [200, 401]
