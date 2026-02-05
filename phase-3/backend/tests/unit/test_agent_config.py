"""T009: Unit tests for OpenRouter client configuration.

Tests that the OpenAI Agents SDK is configured to route through OpenRouter
using set_default_openai_client with AsyncOpenAI.
"""

import os
from unittest.mock import patch, MagicMock

import pytest


@pytest.mark.unit
class TestOpenRouterConfiguration:
    """Tests for Agent + OpenRouter configuration."""

    def test_openrouter_base_url_set(self) -> None:
        """Verify AsyncOpenAI client uses OpenRouter base URL."""
        with patch.dict(os.environ, {
            "OPENROUTER_API_KEY": "test-key-123",
            "OPENROUTER_MODEL": "anthropic/claude-sonnet-4-20250514",
        }):
            from phase3_backend.agent.config import get_openrouter_client

            client = get_openrouter_client()
            assert str(client.base_url).rstrip("/") == "https://openrouter.ai/api/v1"

    def test_openrouter_api_key_from_env(self) -> None:
        """Verify API key is read from OPENROUTER_API_KEY env var."""
        with patch.dict(os.environ, {
            "OPENROUTER_API_KEY": "sk-or-test-key-abc",
            "OPENROUTER_MODEL": "anthropic/claude-sonnet-4-20250514",
        }):
            from phase3_backend.agent.config import get_openrouter_client

            client = get_openrouter_client()
            assert client.api_key == "sk-or-test-key-abc"

    def test_default_model_from_env(self) -> None:
        """Verify model name is read from OPENROUTER_MODEL env var."""
        with patch.dict(os.environ, {
            "OPENROUTER_API_KEY": "test-key",
            "OPENROUTER_MODEL": "google/gemini-2.0-flash-001",
        }):
            from phase3_backend.agent.config import get_model_name

            assert get_model_name() == "google/gemini-2.0-flash-001"

    def test_missing_api_key_raises(self) -> None:
        """Verify ValueError raised when OPENROUTER_API_KEY is missing."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove the key if it exists
            os.environ.pop("OPENROUTER_API_KEY", None)
            with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
                from phase3_backend.agent.config import get_openrouter_client
                # Force re-import to trigger validation
                import importlib
                import phase3_backend.agent.config as config_mod
                importlib.reload(config_mod)
                config_mod.get_openrouter_client()
