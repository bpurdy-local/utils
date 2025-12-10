# =============================================================================
# Dockerfile - Python Application Template
# =============================================================================
# Multi-stage build for smaller production images

# -----------------------------------------------------------------------------
# BUILD STAGE
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Or if using pyproject.toml:
# COPY pyproject.toml .

RUN pip install --target=/app/dependencies -r requirements.txt
# Or: pip install --target=/app/dependencies .

# -----------------------------------------------------------------------------
# PRODUCTION STAGE
# -----------------------------------------------------------------------------
FROM python:3.11-slim as production

# Labels
LABEL maintainer="your.email@example.com" \
      version="1.0.0" \
      description="Your application description"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/dependencies \
    PATH="/app/dependencies/bin:$PATH" \
    # App-specific
    APP_ENV=production \
    PORT=8000

# Create non-root user for security
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/dependencies /app/dependencies

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Alternative commands:
# CMD ["python", "main.py"]
# CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app"]


# -----------------------------------------------------------------------------
# DEVELOPMENT STAGE (optional)
# -----------------------------------------------------------------------------
FROM python:3.11-slim as development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dev dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Copy and install all dependencies (including dev)
COPY requirements.txt requirements-dev.txt* ./
RUN pip install -r requirements.txt \
    && if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# Mount source code as volume in docker-compose
# COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
