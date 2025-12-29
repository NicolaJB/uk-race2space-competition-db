# =========================
# Stage 1: Build Frontend
# =========================
FROM node:20-alpine AS frontend-build

# Set working directory
WORKDIR /app/frontend

# Copy frontend code
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# =========================
# Stage 2: Build Backend
# =========================
FROM python:3.11-slim AS backend-build

# Set working directory
WORKDIR /app/backend

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# =========================
# Stage 3: Combine Frontend + Backend
# =========================
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Copy backend
COPY --from=backend-build /app/backend /app/backend

# Copy frontend build
COPY --from=frontend-build /app/frontend/.next /app/frontend/.next
COPY --from=frontend-build /app/frontend/public /app/frontend/public
COPY --from=frontend-build /app/frontend/package*.json /app/frontend/

# Install Uvicorn for serving FastAPI
RUN pip install --no-cache-dir uvicorn fastapi

# Set environment variables
ENV PORT=8000

# Expose port
EXPOSE 8000

# Command to run backend (FastAPI) on container start
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
