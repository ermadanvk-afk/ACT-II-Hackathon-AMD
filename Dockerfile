FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files to the container
COPY . .

# Hugging Face Spaces exposes port 7860 by default
ENV PORT=7860
EXPOSE 7860

# Start the FastAPI Uvicorn server
CMD ["uvicorn", "Backend.main_orchestrator:app", "--host", "0.0.0.0", "--port", "7860"]
