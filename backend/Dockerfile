FROM python:3.10-slim

# Set environment variable
ENV PYTHONUNBUFFERED=1

# Create and set working directory
WORKDIR /app

# Install only the necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]
