# Hugging Face Spaces - FastAPI Todo API
# Multi-stage build for smaller production image

# Build stage
FROM python:3.13-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Production stage
FROM python:3.13-slim as production

WORKDIR /app

# Create non-root user (required for Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /home/user/.local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /home/user/.local/bin

# Copy application code and migrations
COPY --chown=user src/ ./src/
COPY --chown=user migrations/ ./migrations/
COPY --chown=user alembic.ini ./

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    PYTHONPATH=/home/user/.local/lib/python3.13/site-packages

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health')" || exit 1

# Run the application on port 7860
CMD ["python", "-c", "from dotenv import load_dotenv; load_dotenv(); import uvicorn; uvicorn.run('src.main:app', host='0.0.0.0', port=7860)"]
