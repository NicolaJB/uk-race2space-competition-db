# =========================
# Stage 1: Build Frontend
# =========================
FROM node:20-alpine AS frontend-build

# Set working directory
WORKDIR /app/frontend

# Copy frontend package files and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy all frontend source code and build
COPY frontend/ ./
RUN npm run build

# =========================
# Stage 2: Build Backend
# =========================
FROM python:3.11-slim AS backend-build

# Set working directory
WORKDIR /app/backend

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./

# =========================
# Stage 3: Final Image (Frontend + Backend + DB)
# =========================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend
COPY --from=backend-build /app/backend /app/backend

# Copy frontend build output
COPY --from=frontend-build /app/frontend/.next /app/frontend/.next
COPY --from=frontend-build /app/frontend/public /app/frontend/public
COPY --from=frontend-build /app/frontend/package*.json /app/frontend/

# Copy SQLite database
COPY backend/race-to-space.db /app/backend/race-to-space.db

# Install Uvicorn and FastAPI (runtime only)
RUN pip install --no-cache-dir uvicorn fastapi

# Set environment variables
ENV PORT=8000

# Expose backend port
EXPOSE 8000

# Run FastAPI backend when container starts
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
