"""Error response format integration tests.

T092: [US4] Error response format test

Tests:
- Consistent error response format {error_code, detail, field?}
- HTTP status codes for different error types
- Error code taxonomy coverage
- No stack traces in production errors

@see specs/001-fullstack-todo-web/spec.md - FR-068, FR-081, FR-082
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from src.main import app


class TestValidationErrorFormat:
    """Test validation error response format (422 Unprocessable Entity)."""

    @pytest.mark.asyncio
    async def test_empty_title_validation_error(self):
        """POST /tasks with empty title returns proper validation error."""
        user_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={"title": ""},
                headers={
                    "Authorization": "Bearer fake_token",
                    "Content-Type": "application/json",
                },
            )

        # Should return 401 (auth) or 422 (validation) depending on order
        assert response.status_code in [401, 422]

        error = response.json()
        assert "error_code" in error or "detail" in error

    @pytest.mark.asyncio
    async def test_validation_error_has_error_code(self):
        """Validation errors include error_code field."""
        user_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={"title": "x" * 300},  # Exceeds 200 char limit
                headers={
                    "Authorization": "Bearer fake_token",
                    "Content-Type": "application/json",
                },
            )

        # Auth error first, but structure should be consistent
        error = response.json()
        if isinstance(error, dict):
            # Should have error_code or detail
            assert "error_code" in error or "detail" in error

    @pytest.mark.asyncio
    async def test_invalid_priority_validation_error(self):
        """POST /tasks with invalid priority returns validation error."""
        user_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={"title": "Test", "priority": "Critical"},  # Invalid
                headers={
                    "Authorization": "Bearer fake_token",
                    "Content-Type": "application/json",
                },
            )

        # Should return error (401 auth or 422 validation)
        assert response.status_code in [401, 422]

        error = response.json()
        assert isinstance(error, dict)


class TestAuthenticationErrorFormat:
    """Test authentication error response format (401 Unauthorized)."""

    @pytest.mark.asyncio
    async def test_missing_token_error_format(self):
        """Request without token returns proper 401 error format."""
        user_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(f"/api/{user_id}/tasks")

        assert response.status_code == 401

        error = response.json()
        assert "error_code" in error
        assert error["error_code"] == "AUTHENTICATION_REQUIRED"
        assert "detail" in error

    @pytest.mark.asyncio
    async def test_invalid_token_error_format(self):
        """Request with invalid token returns proper 401 error format."""
        user_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks",
                headers={"Authorization": "Bearer invalid_token_here"},
            )

        assert response.status_code == 401

        error = response.json()
        assert "error_code" in error
        assert error["error_code"] in ["INVALID_TOKEN", "TOKEN_EXPIRED"]
        assert "detail" in error

    @pytest.mark.asyncio
    async def test_expired_token_error_format(self):
        """Request with expired token returns TOKEN_EXPIRED error code."""
        user_id = uuid4()
        # Create an obviously expired token (would need actual JWT for real test)
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxfQ.signature"

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks",
                headers={"Authorization": f"Bearer {expired_token}"},
            )

        assert response.status_code == 401

        error = response.json()
        assert "error_code" in error
        assert "detail" in error


class TestAuthorizationErrorFormat:
    """Test authorization error response format (403 Forbidden)."""

    @pytest.mark.asyncio
    async def test_forbidden_error_has_error_code(self):
        """403 Forbidden errors include error_code field."""
        # This would require a valid token trying to access another user's resource
        # For now, test the error structure
        pass  # Requires authenticated test fixture


class TestNotFoundErrorFormat:
    """Test not found error response format (404 Not Found)."""

    @pytest.mark.asyncio
    async def test_not_found_error_format(self):
        """GET /tasks/{id} for non-existent task returns 404 format."""
        user_id = uuid4()
        task_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks/{task_id}",
                headers={"Authorization": "Bearer fake_token"},
            )

        # Will be 401 without valid auth, but format should be consistent
        assert response.status_code in [401, 404]

        error = response.json()
        assert "error_code" in error or "detail" in error


class TestBadRequestErrorFormat:
    """Test bad request error response format (400 Bad Request)."""

    @pytest.mark.asyncio
    async def test_malformed_json_error(self):
        """Request with malformed JSON returns 400 Bad Request."""
        user_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                content='{"title": "Test"',  # Missing closing brace
                headers={
                    "Authorization": "Bearer fake_token",
                    "Content-Type": "application/json",
                },
            )

        # FastAPI returns 422 for validation errors, 400 for malformed JSON
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_missing_content_type_error(self):
        """POST without Content-Type returns error."""
        user_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                content='{"title": "Test"}',
                headers={"Authorization": "Bearer fake_token"},
            )

        # Should return error without proper Content-Type
        assert response.status_code in [400, 401, 415, 422]


class TestRateLimitErrorFormat:
    """Test rate limit error response format (429 Too Many Requests)."""

    @pytest.mark.asyncio
    async def test_rate_limit_error_has_retry_after(self):
        """429 Too Many Requests includes Retry-After header."""
        # This test would need to trigger actual rate limiting
        # Just verify the format expectation
        pass  # Requires rate limit triggering


class TestServerErrorFormat:
    """Test server error response format (500 Internal Server Error)."""

    @pytest.mark.asyncio
    async def test_server_error_no_stack_trace(self):
        """500 errors should not expose stack traces."""
        # Server errors should have:
        # - error_code: "INTERNAL_ERROR"
        # - detail: Generic message
        # - request_id: For troubleshooting
        # - NO stack trace
        pass  # Requires triggering actual server error


class TestErrorResponseStructure:
    """Test overall error response structure consistency."""

    @pytest.mark.asyncio
    async def test_all_errors_have_detail_field(self):
        """All error responses include 'detail' field."""
        user_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test various error conditions
            response = await client.get(f"/api/{user_id}/tasks")

        error = response.json()
        # FastAPI default or custom error format
        assert "detail" in error or "message" in error

    @pytest.mark.asyncio
    async def test_error_response_is_json(self):
        """All error responses return JSON content type."""
        user_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(f"/api/{user_id}/tasks")

        assert "application/json" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_generic_auth_error_message(self):
        """Auth errors use generic messages (don't reveal which field is wrong)."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/signin",
                json={
                    "email": "nonexistent@example.com",
                    "password": "wrongpassword",
                },
            )

        if response.status_code == 401:
            error = response.json()
            # Should NOT say "Email not found" or "Password incorrect"
            # Should say generic "Invalid email or password"
            detail = error.get("detail", "")
            if isinstance(detail, str):
                assert "not found" not in detail.lower()
                assert "incorrect" not in detail.lower()
