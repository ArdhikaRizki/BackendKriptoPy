# Use an official Python slim image
FROM python:3.11-slim

# Install system dependencies needed by Pillow and build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libjpeg-dev \
       zlib1g-dev \
       libfreetype6-dev \
       liblcms2-dev \
       libwebp-dev \
       libopenjp2-7-dev \
       libtiff5-dev \
       libpng-dev \
       git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files first to leverage Docker layer caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose the default Flask port (config.py default: 5000)
EXPOSE 5000

# Environment defaults (can be overridden at runtime)
ENV FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000 \
    FLASK_DEBUG=False \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Use a simple, portable command to start the app
CMD ["python", "main.py"]
