# Jatan Jewellery - Salary Management System
# Multi-stage Docker build for production deployment

FROM python:3.12-slim as base

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  DEBIAN_FRONTEND=noninteractive

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  postgresql-client \
  curl \
  gcc \
  python3-dev \
  libpq-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/backups /app/exports /app/certificates

# Set permissions
RUN chmod +x scripts/*.sh 2>/dev/null || true

# Expose application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import psycopg2; print('OK')" || exit 1

# Default command (can be overridden in docker-compose.yml)
CMD ["python", "run_postgres_app.py"]

