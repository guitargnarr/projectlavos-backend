FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY phishing_service.py .

# Create models directory
RUN mkdir -p /app/models

# Expose port
EXPOSE 9001

# Run the service
CMD ["python", "phishing_service.py"]