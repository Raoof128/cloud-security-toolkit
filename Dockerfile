# Cloud Security Toolkit - Docker Image
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

LABEL maintainer="Cloud Security Toolkit Contributors"
LABEL description="Automated cloud security auditing and hardening toolkit"
LABEL version="2.0.0"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash scanner && \
    mkdir -p /app /reports /config && \
    chown -R scanner:scanner /app /reports /config

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=scanner:scanner . .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AWS_DEFAULT_REGION=us-east-1

# Switch to non-root user
USER scanner

# Create directories for outputs
RUN mkdir -p /app/reports

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import boto3; print('healthy')" || exit 1

# Default command (can be overridden)
ENTRYPOINT ["python", "cloud_security_audit.py"]
CMD ["--help"]

# Volume for reports
VOLUME ["/app/reports"]

# Expose port if running in server mode (future feature)
# EXPOSE 8080

# Usage examples:
# docker run cloud-security-toolkit --demo
# docker run -v ~/.aws:/home/scanner/.aws:ro cloud-security-toolkit --provider aws
# docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY cloud-security-toolkit --provider aws
