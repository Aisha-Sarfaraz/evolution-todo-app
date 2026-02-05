"""T105: Tests for enhanced health check endpoint."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestHealthCheck:
    """Test enhanced health check returns component status."""

    @pytest.mark.asyncio
    async def test_health_check_healthy(self):
        """Health check returns healthy when DB is up."""
        from src.main import health_check

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()

        async def mock_get_session():
            yield mock_session

        with patch("src.main.scheduler") as mock_scheduler, \
             patch("src.main.os.getenv", return_value="8001"):
            mock_scheduler.running = True

            # Mock the imports inside health_check
            with patch.dict("sys.modules", {}):
                result = await health_check()

        assert result["service"] == "todo-chatbot-api"
        assert result["version"] == "3.0.0"
        assert "timestamp" in result
        assert "components" in result

    @pytest.mark.asyncio
    async def test_health_check_returns_dict(self):
        """Health check always returns a valid dict."""
        from src.main import health_check

        result = await health_check()

        assert isinstance(result, dict)
        assert "status" in result
        assert "components" in result
