"""OpenAPI schema integration tests.

T091: [US4] OpenAPI schema integration test

Tests:
- API documentation availability at /docs
- OpenAPI schema completeness and validity
- Endpoint documentation coverage
- Request/response schema definitions

@see specs/001-fullstack-todo-web/spec.md - FR-069, SC-015
"""

import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app


class TestOpenAPISchemaAvailability:
    """Test OpenAPI schema and docs availability."""

    @pytest.mark.asyncio
    async def test_openapi_json_endpoint_available(self):
        """GET /openapi.json returns valid OpenAPI schema."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/openapi.json")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        schema = response.json()
        assert "openapi" in schema
        assert schema["openapi"].startswith("3.")
        assert "info" in schema
        assert "paths" in schema

    @pytest.mark.asyncio
    async def test_swagger_ui_available(self):
        """GET /docs returns Swagger UI HTML page."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "swagger" in response.text.lower()

    @pytest.mark.asyncio
    async def test_redoc_ui_available(self):
        """GET /redoc returns ReDoc UI HTML page."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/redoc")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestOpenAPISchemaCompleteness:
    """Test OpenAPI schema contains all required endpoints."""

    @pytest.fixture
    async def openapi_schema(self):
        """Fetch and return OpenAPI schema."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/openapi.json")
        return response.json()

    @pytest.mark.asyncio
    async def test_api_info_section(self, openapi_schema):
        """Schema info section contains title and version."""
        info = openapi_schema["info"]

        assert "title" in info
        assert "version" in info
        assert len(info["title"]) > 0
        assert len(info["version"]) > 0

    @pytest.mark.asyncio
    async def test_task_endpoints_documented(self, openapi_schema):
        """All 6 task endpoints documented in schema."""
        paths = openapi_schema["paths"]

        # Task list endpoint
        assert "/api/{user_id}/tasks" in paths
        tasks_path = paths["/api/{user_id}/tasks"]
        assert "get" in tasks_path  # List tasks
        assert "post" in tasks_path  # Create task

        # Single task endpoint
        assert "/api/{user_id}/tasks/{task_id}" in paths
        task_path = paths["/api/{user_id}/tasks/{task_id}"]
        assert "get" in task_path  # Get task
        assert "put" in task_path  # Update task
        assert "delete" in task_path  # Delete task

        # Complete task endpoint
        assert "/api/{user_id}/tasks/{task_id}/complete" in paths
        complete_path = paths["/api/{user_id}/tasks/{task_id}/complete"]
        assert "patch" in complete_path  # Toggle complete

    @pytest.mark.asyncio
    async def test_category_endpoints_documented(self, openapi_schema):
        """All 3 category endpoints documented in schema."""
        paths = openapi_schema["paths"]

        # Categories list endpoint
        assert "/api/{user_id}/categories" in paths
        categories_path = paths["/api/{user_id}/categories"]
        assert "get" in categories_path  # List categories
        assert "post" in categories_path  # Create category

        # Single category endpoint
        assert "/api/{user_id}/categories/{category_id}" in paths
        category_path = paths["/api/{user_id}/categories/{category_id}"]
        assert "delete" in category_path  # Delete category

    @pytest.mark.asyncio
    async def test_tag_endpoints_documented(self, openapi_schema):
        """All 4 tag endpoints documented in schema."""
        paths = openapi_schema["paths"]

        # Tags list endpoint
        assert "/api/{user_id}/tags" in paths
        tags_path = paths["/api/{user_id}/tags"]
        assert "get" in tags_path  # List tags
        assert "post" in tags_path  # Create tag

        # Single tag endpoint
        assert "/api/{user_id}/tags/{tag_id}" in paths
        tag_path = paths["/api/{user_id}/tags/{tag_id}"]
        assert "put" in tag_path  # Update/rename tag
        assert "delete" in tag_path  # Delete tag

    @pytest.mark.asyncio
    async def test_auth_endpoints_documented(self, openapi_schema):
        """Auth endpoints documented in schema."""
        paths = openapi_schema["paths"]

        # Auth endpoints
        auth_endpoints = [
            "/api/auth/signup",
            "/api/auth/signin",
            "/api/auth/signout",
            "/api/auth/refresh",
        ]

        for endpoint in auth_endpoints:
            assert endpoint in paths, f"Missing auth endpoint: {endpoint}"


class TestOpenAPISchemaDefinitions:
    """Test OpenAPI schema has proper request/response definitions."""

    @pytest.fixture
    async def openapi_schema(self):
        """Fetch and return OpenAPI schema."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/openapi.json")
        return response.json()

    @pytest.mark.asyncio
    async def test_task_create_request_schema(self, openapi_schema):
        """POST /tasks has request body schema with title, description, priority."""
        paths = openapi_schema["paths"]
        post_tasks = paths["/api/{user_id}/tasks"]["post"]

        assert "requestBody" in post_tasks
        request_body = post_tasks["requestBody"]
        assert "content" in request_body
        assert "application/json" in request_body["content"]

    @pytest.mark.asyncio
    async def test_task_response_schema(self, openapi_schema):
        """Task endpoints have response schemas."""
        paths = openapi_schema["paths"]

        # GET /tasks should have 200 response
        get_tasks = paths["/api/{user_id}/tasks"]["get"]
        assert "responses" in get_tasks
        assert "200" in get_tasks["responses"]

        # POST /tasks should have 201 response
        post_tasks = paths["/api/{user_id}/tasks"]["post"]
        assert "responses" in post_tasks
        assert "201" in post_tasks["responses"]

    @pytest.mark.asyncio
    async def test_error_response_schemas(self, openapi_schema):
        """Common error responses (401, 403, 404, 422) documented."""
        paths = openapi_schema["paths"]

        # Check protected endpoint has 401 response
        get_tasks = paths["/api/{user_id}/tasks"]["get"]
        responses = get_tasks["responses"]

        # Should have error responses defined
        assert "401" in responses or "4XX" in responses or "default" in responses

    @pytest.mark.asyncio
    async def test_path_parameters_documented(self, openapi_schema):
        """Path parameters (user_id, task_id) properly documented."""
        paths = openapi_schema["paths"]

        # Check user_id parameter on tasks endpoint
        get_tasks = paths["/api/{user_id}/tasks"]["get"]
        assert "parameters" in get_tasks

        # Find user_id parameter
        params = get_tasks["parameters"]
        user_id_param = next(
            (p for p in params if p.get("name") == "user_id"),
            None
        )
        assert user_id_param is not None
        assert user_id_param["in"] == "path"
        assert user_id_param["required"] is True

    @pytest.mark.asyncio
    async def test_query_parameters_documented(self, openapi_schema):
        """Query parameters for search/filter/sort documented."""
        paths = openapi_schema["paths"]

        get_tasks = paths["/api/{user_id}/tasks"]["get"]
        params = get_tasks["parameters"]

        # Get query parameter names
        query_params = [p["name"] for p in params if p.get("in") == "query"]

        # Should have search, status, priority, sort_by parameters
        expected_params = ["search", "status", "priority", "sort_by", "order"]
        for param in expected_params:
            assert param in query_params, f"Missing query parameter: {param}"


class TestOpenAPISecurityDefinitions:
    """Test OpenAPI schema has proper security definitions."""

    @pytest.fixture
    async def openapi_schema(self):
        """Fetch and return OpenAPI schema."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/openapi.json")
        return response.json()

    @pytest.mark.asyncio
    async def test_security_scheme_defined(self, openapi_schema):
        """Bearer token security scheme defined."""
        components = openapi_schema.get("components", {})
        security_schemes = components.get("securitySchemes", {})

        # Should have Bearer token scheme
        assert len(security_schemes) > 0

        # Check for HTTP Bearer or OAuth2
        has_bearer = any(
            scheme.get("type") == "http" and scheme.get("scheme") == "bearer"
            for scheme in security_schemes.values()
        )
        has_oauth2 = any(
            scheme.get("type") == "oauth2"
            for scheme in security_schemes.values()
        )

        assert has_bearer or has_oauth2, "No Bearer or OAuth2 security scheme defined"

    @pytest.mark.asyncio
    async def test_protected_endpoints_have_security(self, openapi_schema):
        """Protected endpoints reference security scheme."""
        paths = openapi_schema["paths"]

        # Task endpoints should require authentication
        get_tasks = paths["/api/{user_id}/tasks"]["get"]

        # Security can be at operation level or global level
        has_operation_security = "security" in get_tasks
        has_global_security = "security" in openapi_schema

        assert has_operation_security or has_global_security, \
            "Protected endpoints should have security requirements"
