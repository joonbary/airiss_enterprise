# AIRISS v4.0 Enhanced - Production Dockerfile
# Multi-stage build for optimized production deployment

# Stage 1: Frontend Build (Node.js)
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ ./

# Build frontend (if React app exists)
RUN if [ -f "package.json" ]; then npm run build; else echo "No React app found, skipping frontend build"; fi

# Stage 2: Python Backend
FROM python:3.11-slim AS backend

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AIRISS_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create airiss user
RUN useradd --create-home --shell /bin/bash airiss

# Set working directory
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY *.py ./
COPY *.ini ./

# Copy built frontend (if exists)
COPY --from=frontend-builder /frontend/build ./static/ || echo "No frontend build found"

# Create necessary directories
RUN mkdir -p logs uploads temp_data && \
    chown -R airiss:airiss /app

# Switch to airiss user
USER airiss

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Expose port
EXPOSE 8002

# Default command
CMD ["python", "-m", "uvicorn", "app.main_enhanced:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"]
