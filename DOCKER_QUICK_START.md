gerowany po angielsku, sprawdź i pop# 🐳 Docker Quick Start Guide

## Overview

This guide provides a quick setup for running Eclesiar application with automated Google Sheets reports every 6 hours.

## Prerequisites

- Docker and Docker Compose installed
- Google Cloud Project with Sheets API enabled
- Google Service Account credentials

## Quick Setup

### 1. Configuration
```bash
# Copy environment template
cp docker.env.template .env

# Edit with your credentials
nano .env
```

### 2. Google Sheets Setup
```bash
# Create cred directory
mkdir -p cred

# Place your Google credentials file
# cred/google_credentials.json
```

### 3. Start Application
```bash
# Make scripts executable
chmod +x start-docker.sh stop-docker.sh

# Start automated reporting
./start-docker.sh
```

## What Happens

1. **First Run**: Immediate report generation
2. **Every 6 Hours**: Automatic Google Sheets report updates
3. **Logging**: All operations logged to `logs/cron.log`
4. **Data Persistence**: All data preserved across restarts

## Management Commands

```bash
# View logs
docker-compose logs -f eclesiar-scheduler

# Stop application
./stop-docker.sh

# Manual report generation
docker-compose exec eclesiar-scheduler python3 main.py google-sheets-report

# Check container health
docker-compose ps
```

## Configuration

Edit `.env` file with your settings:
- `AUTH_TOKEN` - Your Eclesiar API token
- `GOOGLE_SHEETS_EXISTING_ID` - Your Google Spreadsheet ID
- `GOOGLE_PROJECT_ID` - Your Google Cloud project ID

## Troubleshooting

1. **Check logs**: `docker-compose logs eclesiar-scheduler`
2. **Verify credentials**: Ensure `cred/google_credentials.json` exists
3. **Test manually**: Run manual report generation
4. **Check permissions**: Ensure Google Sheets API access

## Support

For detailed setup instructions, see [DOCKER_SETUP.md](DOCKER_SETUP.md).

---

**Copyright (c) 2025 Teo693**  
**Licensed under the MIT License**
