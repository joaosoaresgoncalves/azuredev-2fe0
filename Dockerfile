# Optional: Dockerfile for standalone deployment
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port for web server
EXPOSE 8000

# Default command (can be overridden)
CMD ["python", "run_model.py"]
