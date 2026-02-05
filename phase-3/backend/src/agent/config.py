"""T014: Agent + OpenRouter configuration module.

Configures OpenAI Agents SDK to route all LLM calls through OpenRouter
using set_default_openai_client with a custom AsyncOpenAI client.
"""

import os

from openai import AsyncOpenAI


def get_openrouter_client() -> AsyncOpenAI:
    """Create an AsyncOpenAI client configured for OpenRouter.

    Reads OPENROUTER_API_KEY from environment.

    Returns:
        AsyncOpenAI client with OpenRouter base URL.

    Raises:
        ValueError: If OPENROUTER_API_KEY is not set.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is required. "
            "Get your key at https://openrouter.ai/keys"
        )

    return AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def get_model_name() -> str:
    """Get the LLM model name from environment.

    Returns:
        Model identifier string (e.g., 'anthropic/claude-sonnet-4-20250514').
    """
    return os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-20250514")


def configure_agent_client() -> None:
    """Configure the OpenAI Agents SDK to use OpenRouter.

    Calls set_default_openai_client to route all Agent SDK LLM calls
    through the OpenRouter API.
    """
    from agents import set_default_openai_client

    client = get_openrouter_client()
    set_default_openai_client(client)
