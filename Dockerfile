# syntax=docker/dockerfile:1.7

# Stage 1: Build Next.js Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 2: Production Monolith Runtime for Hugging Face Spaces
FROM python:3.11.9-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000 \
    DATABASE_URL="sqlite:////home/user/app/atmosiq.db" \
    HOME="/home/user" \
    PATH="/home/user/.local/bin:$PATH"

# Install system dependencies & Node.js 20 runtime for Next.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    gnupg \
    libpq-dev \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create non-root Hugging Face user (UID 1000)
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

# Install Python backend package & ML dependencies
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

# Copy application configuration and metadata
COPY config ./config
COPY data_schema ./data_schema
COPY alembic.ini ./
COPY alembic ./alembic
RUN mkdir -p artifacts logs

# Copy Next.js production build from Stage 1
COPY --from=frontend-builder /app/frontend/package.json ./frontend/package.json
COPY --from=frontend-builder /app/frontend/node_modules ./frontend/node_modules
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/next.config.ts ./frontend/next.config.ts

# Copy entrypoint script and set permissions
COPY docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh && chown -R user:user /home/user

USER user
EXPOSE 10000 7860 8000

CMD ["./entrypoint.sh"]
