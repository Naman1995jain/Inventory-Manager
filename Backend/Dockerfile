# Multi-stage Dockerfile for Python Backend
# Stage 1: Base image with dependencies
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface \
    HF_HOME=/home/appuser/.cache/huggingface

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: Production image
FROM base AS production

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /home/appuser -m appuser

# Create logs directory and set up home directory with proper permissions
RUN mkdir -p /app/logs /home/appuser/.cache && \
    chown -R appuser:appuser /app /home/appuser && \
    chmod -R 755 /app && \
    chmod 777 /app/logs && \
    chmod -R 755 /home/appuser

# Copy and make initialization script executable
# Copy entrypoint script
COPY docker-entrypoint.sh /app/
# Fix line endings and make executable (in case the script was created on Windows)
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use custom entrypoint that sets up database first
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command
CMD ["python", "main.py"]