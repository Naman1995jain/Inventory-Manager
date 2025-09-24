# Multi-stage Dockerfile for Python Backend
# Stage 1: Base image with dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: Production image
FROM base as production

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs && chmod 755 /app/logs

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -s /bin/false appuser && \
    chown -R appuser:appuser /app

# Copy and make initialization script executable
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

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