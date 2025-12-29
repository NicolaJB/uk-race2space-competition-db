# =========================
# Stage 1: Frontend Build
# =========================
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend

# Copy only package files and install dependencies
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
WORKDIR /app/backend

# Copy backend from build stage
COPY --from=backend-build /app/backend /app/backend

# Copy frontend build (for static file serving)
COPY --from=frontend-build /app/frontend/.next /app/frontend/.next
COPY --from=frontend-build /app/frontend/public /app/frontend/public

# Copy SQLite database
COPY backend/race-to-space.db /app/backend/race-to-space.db

# Expose port for Render
ENV PORT=10000
EXPOSE $PORT

# Start FastAPI with uvicorn
RUN pip install --no-cache-dir uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
