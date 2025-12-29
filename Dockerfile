# =========================
# Stage 1: Frontend Build
# =========================
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy source and build
COPY frontend/ ./
RUN npm run build

# =========================
# Stage 2: Backend Build
# =========================
FROM python:3.11-slim AS backend-build
WORKDIR /app/backend

# =========================
# Stage 1: Frontend Build
# =========================
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# =========================
# Stage 2: Backend Build
# =========================
FROM python:3.11-slim AS backend-build
WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

# =========================
# Stage 3: Final Image
# =========================
FROM python:3.11-slim
WORKDIR /app/backend

# Copy backend
COPY --from=backend-build /app/backend /app/backend

# Copy frontend build (Next.js static files)
COPY --from=frontend-build /app/frontend/.next /app/frontend/.next
COPY --from=frontend-build /app/frontend/public /app/frontend/public

# Copy SQLite database
COPY backend/race-to-space.db /app/backend/race-to-space.db

# Expose port for Render
ENV PORT=10000
EXPOSE $PORT

# Start FastAPI using Render's assigned port
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
