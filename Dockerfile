FROM node:20-alpine AS frontend
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY src/ ./src/
COPY static/ ./static/
COPY svelte.config.js vite.config.ts tsconfig.json ./
RUN npm run build

FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev
COPY backend/*.py ./
COPY --from=frontend /app/build ./static

CMD uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
