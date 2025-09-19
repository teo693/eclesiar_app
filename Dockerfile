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

# Create symlink for python -> python3 to avoid 'python: not found' errors
RUN ln -sf /usr/local/bin/python3 /usr/local/bin/python

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
RUN echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" > /etc/cron.d/eclesiar-cron && \
    echo "0 */3 * * * root cd /app && PATH=/usr/local/bin:\$PATH /usr/local/bin/python3 main.py google-sheets-report --economic-only >> /app/logs/cron.log 2>&1" >> /etc/cron.d/eclesiar-cron && \
    chmod 0644 /etc/cron.d/eclesiar-cron && \
    crontab /etc/cron.d/eclesiar-cron

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Eclesiar App with scheduled reports..."\n\
echo "Google Sheets economic reports will be generated every 3 hours"\n\
echo "First report will be generated immediately..."\n\
echo "Starting periodic command scheduler: cron."\n\
\n\
# Ensure log file exists\n\
touch /app/logs/cron.log\n\
\n\
# Start cron daemon\n\
service cron start\n\
\n\
# Show cron configuration for debugging\n\
echo "Cron configuration:"\n\
crontab -l\n\
\n\
# Generate initial report\n\
cd /app && /usr/local/bin/python3 main.py google-sheets-report --economic-only\n\
\n\
# Keep container running and show logs\n\
tail -f /app/logs/cron.log' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose port (if needed for future web interface)
EXPOSE 8000

# Set the startup script as entrypoint
ENTRYPOINT ["/app/start.sh"]
