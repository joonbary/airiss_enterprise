# AIRISS v4.0 Production Dockerfile
# Multi-stage build for optimized production image

# ================================
# Stage 1: Python Dependencies
# ================================
FROM python:3.10-slim as python-deps

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

# ================================
# Stage 2: Node.js Dependencies (Frontend)
# ================================
FROM node:18-alpine as node-deps

WORKDIR /app/frontend

# Copy package files
COPY airiss-v4-frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code and build
COPY airiss-v4-frontend/ ./
RUN npm run build

# ================================
# Stage 3: Production Image
# ================================
FROM python:3.10-slim as production

# Metadata
LABEL maintainer="AIRISS Team <airiss-dev@okfinancial.com>" \
      version="4.0.0" \
      description="AIRISS - AI-based Intelligent Rating & Insight Scoring System" \
      org.opencontainers.image.title="AIRISS v4.0" \
      org.opencontainers.image.description="AI 기반 직원 성과/역량 스코어링 시스템" \
      org.opencontainers.image.vendor="OK Financial Group" \
      org.opencontainers.image.version="4.0.0" \
      org.opencontainers.image.url="https://github.com/joonbary/airiss_enterprise" \
      org.opencontainers.image.source="https://github.com/joonbary/airiss_enterprise"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    ENVIRONMENT=production \
    APP_MODULE=app.main:app \
    PORT=8002

# Install system dependencies for production
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash airiss && \
    mkdir -p /app && \
    chown -R airiss:airiss /app

# Copy virtual environment from python-deps stage
COPY --from=python-deps /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=airiss:airiss . .

# Copy built frontend from node-deps stage
COPY --from=node-deps --chown=airiss:airiss /app/frontend/build ./static/frontend/

# Create necessary directories
RUN mkdir -p logs uploads temp_data && \
    chown -R airiss:airiss logs uploads temp_data

# Switch to non-root user
USER airiss

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "4"]

# ================================
# Development Stage (optional)
# ================================
FROM production as development

# Switch back to root for development setup
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install -r /tmp/requirements-dev.txt

# Switch back to airiss user
USER airiss

# Development command with hot reload
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
