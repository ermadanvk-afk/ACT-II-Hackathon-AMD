FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed (e.g., sqlite3)
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY . .

# Render/HF typically use the $PORT environment variable, defaulting to 8000
ENV PORT=8000

# Start the FastAPI Uvicorn server, using the injected PORT env var
CMD ["sh", "-c", "uvicorn Backend.main_orchestrator:app --host 0.0.0.0 --port ${PORT:-8000}"]
