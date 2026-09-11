# Multi-Stage Build for Zero-Trust CI/CD Pipeline Validator
# Stage 1: Build React SOC Dashboard
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Security Backend & Standalone CLI
FROM python:3.11-slim AS runtime
WORKDIR /app

# Install git and essential system security tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend and validator code
COPY backend/ /app/backend/
COPY validator/ /app/validator/
COPY configs/ /app/configs/
COPY demo/ /app/demo/
COPY pytest.ini /app/pytest.ini

# Copy compiled frontend from Stage 1 into backend's static directory
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Install CLI binary alias
RUN ln -s /app/validator/cli.py /usr/local/bin/zt-validator && chmod +x /app/validator/cli.py /usr/local/bin/zt-validator

# Environment configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ZT_CONFIG_DIR=/app/configs \
    ZT_DB_PATH=/app/validator.db \
    ZT_LOG_DIR=/app/logs

EXPOSE 8000

# Default entrypoint starts the FastAPI dashboard and API server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
