FROM python:3.11-slim

# Basis hygiene
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY backup.py .
COPY config.py .

# Data directory (volume)
VOLUME ["/data"]

# Default command
CMD ["python", "backup.py"]
