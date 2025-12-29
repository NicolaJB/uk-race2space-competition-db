# =========================
# Stage 1: Frontend Build
# =========================
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy full frontend source and build
COPY frontend/ ./
RUN npm run build

# =========================
# Stage 2: Backend Build
# =========================
FROM python:3.11-slim AS backend-build
WORKDIR /app/backend

# Copy requirements and install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# =========================
# Stage 3: Final Image
# =========================
FROM python:3.11-slim
WORKDIR /app

# Install uvicorn for FastAPI
RUN pip install --no-cache-dir uvicorn

# Copy backend
COPY --from=backend-build /app/backend /app/backend

# Copy frontend build for static serving
COPY --from=frontend-build /app/frontend/.next /app/frontend/.next
COPY --from=frontend-build /app/frontend/public /app/frontend/public

# Copy SQLite database
COPY backend/race-to-space.db /app/backend/race-to-space.db

# Set working directory for FastAPI app
WORKDIR /app/backend

# Use Render’s PORT environment variable
ENV PORT=10000
EXPOSE $PORT

# Start FastAPI with uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
