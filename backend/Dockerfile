# Stage 1: Building the dependencies
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Building the final image
FROM python:3.11-slim

# Set labels for better container metadata
LABEL maintainer="support@example.com" \
      version="1.0.0" \
      description="Agentic Character Chatbot API"

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PORT=8000

# Create a non-root user and switch to it
RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser -m appuser \
    && chown -R appuser:appuser /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copy application code
COPY . .

# Create required directories with appropriate permissions
RUN mkdir -p /app/character_data /app/dynamic_tools \
    && chown -R appuser:appuser /app/character_data /app/dynamic_tools

# Switch to non-root user
USER appuser

# Create health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose application port
EXPOSE ${PORT}

# Define entrypoint
ENTRYPOINT ["python", "run.py"]
