---
title: Todo AI Chatbot API
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Todo AI Chatbot API

AI-powered conversational task management backend using OpenAI Agents SDK with Gemini via LiteLLM.

## Features

- **Natural Language Task Management**: Create, list, update, and complete tasks via chat
- **MCP Tools Integration**: Model Context Protocol tools for task operations
- **SSE Streaming**: Real-time streaming responses via Server-Sent Events
- **Conversation Persistence**: Thread-based conversation history
- **Recurrence & Reminders**: Scheduled task management

## API Endpoints

- `POST /api/chatkit` - ChatKit-compatible chat endpoint (SSE streaming)
- `POST /api/chat` - Standard chat endpoint
- `GET /health` - Health check

## Environment Variables

Required environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENROUTER_API_KEY` - OpenRouter API key for LLM access
- `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated)

## Architecture

```
Frontend (ChatKit) → /api/chatkit → OpenAI Agents SDK → MCP Tools → Database
```

Built with:
- FastAPI
- OpenAI Agents SDK + LiteLLM
- MCP (Model Context Protocol)
- PostgreSQL (Neon)
- APScheduler
