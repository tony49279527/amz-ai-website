# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Expose port (Cloud Run defaults to 8080)
EXPOSE 8080

# Start the server
CMD ["uvicorn", "discovery_service.main:app", "--host", "0.0.0.0", "--port", "8080"]
