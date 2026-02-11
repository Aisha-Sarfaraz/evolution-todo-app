# Phase IV: Backend Multi-Stage Docker Build
# Build context: phase-3/backend/
# Usage: docker build -t todo-backend:latest -f phase-4/docker/backend.Dockerfile phase-3/backend/

# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies for psycopg2 and asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a clean prefix
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Production ---
FROM python:3.11-slim AS production

# Install runtime-only dependency for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash appuser

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install/lib /usr/local/lib

# Copy application code
COPY src/ ./src/

# Copy alembic config if it exists (wildcard COPY is a no-op when no match)
# migration-job.yaml uses this image for `alembic upgrade head`
COPY alembic.in[i] ./

# Set ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
