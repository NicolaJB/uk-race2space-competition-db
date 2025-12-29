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

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# =========================
# Stage 3: Final Image
# =========================
FROM python:3.11-slim
WORKDIR /app/backend

# Install Python dependencies again in final stage (ensures uvicorn exists)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY --from=backend-build /app/backend /app/backend

# Copy frontend build output
COPY --from=frontend-build /app/frontend/.next /app/frontend/.next
COPY --from=frontend-build /app/frontend/public /app/frontend/public

# Copy SQLite database
COPY backend/race-to-space.db /app/backend/race-to-space.db

# Expose Render PORT
ENV PORT=10000
EXPOSE $PORT

# Run FastAPI via uvicorn
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
