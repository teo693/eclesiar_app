# Eclesiar App Dockerfile
# Copyright (c) 2025 Teo693
# Licensed under the MIT License - see LICENSE file for details.

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/base.txt /app/requirements/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/base.txt

# Copy application code
COPY . /app/

# Force cache invalidation for Google Sheets implementation
RUN echo "Google Sheets implementation updated: $(date)" > /app/.build_cache

# Create necessary directories
RUN mkdir -p /app/logs /app/reports /app/data /app/cred

# Set proper permissions
RUN chmod +x /app/main.py

# Create cron job for Google Sheets economic reports every 3 hours  
RUN echo "0 */3 * * * cd /app && python3 main.py google-sheets-report --economic-only >> /app/logs/cron.log 2>&1" | crontab -

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Eclesiar App with scheduled reports..."\n\
echo "Google Sheets economic reports will be generated every 3 hours"\n\
echo "First report will be generated immediately..."\n\
\n\
# Start cron daemon\n\
service cron start\n\
\n\
# Generate initial report\n\
cd /app && python3 main.py google-sheets-report --economic-only\n\
\n\
# Keep container running and show logs\n\
tail -f /app/logs/cron.log' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose port (if needed for future web interface)
EXPOSE 8000

# Set the startup script as entrypoint
ENTRYPOINT ["/app/start.sh"]
