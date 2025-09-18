# 🐳 Eclesiar App - Docker Setup Guide

## 📋 Overview

This guide explains how to set up the Eclesiar application to run automatically in Docker, generating Google Sheets reports every 6 hours.

## 🚀 Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Google Cloud Project with Sheets API enabled
- Google Service Account credentials

### 2. Configuration

1. **Copy environment template:**
   ```bash
   cp docker.env.template .env
   ```

2. **Edit `.env` file with your settings:**
   ```bash
   nano .env
   ```

3. **Configure Google Sheets:**
   - Set `GOOGLE_PROJECT_ID` to your Google Cloud project ID
   - Set `GOOGLE_SERVICE_ACCOUNT_EMAIL` to your service account email
   - Set `GOOGLE_SHEETS_EXISTING_ID` to your existing spreadsheet ID (optional)
   - Place your `google_credentials.json` file in the `cred/` directory

4. **Configure API access:**
   - Set `AUTH_TOKEN` to your Eclesiar API token

### 3. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the scheduler
docker-compose up -d

# View logs
docker-compose logs -f eclesiar-scheduler
```

## 📊 How It Works

### Automatic Scheduling

The container runs a cron job that executes every 6 hours:
```bash
0 */6 * * * cd /app && python3 main.py google-sheets-report >> /app/logs/cron.log 2>&1
```

### Report Generation

Each scheduled run will:
1. Fetch fresh data from the Eclesiar API
2. Generate a comprehensive report with all sections:
   - ⚔️ Military data (wars, statistics)
   - 🏆 Warriors data (heroes ranking)
   - 💰 Economic data (currency rates, job offers)
   - 🏭 Production analysis (regional productivity)
3. Upload the report to Google Sheets
4. Log the results

### Data Persistence

The following directories are mounted as volumes:
- `./data/` - Database and persistent data
- `./logs/` - Application and cron logs
- `./reports/` - Generated reports (if any)
- `./cred/` - Credentials and configuration files

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SCHEDULE_INTERVAL_HOURS` | Report generation interval | `6` |
| `REPORT_SECTIONS_MILITARY` | Include military section | `true` |
| `REPORT_SECTIONS_WARRIORS` | Include warriors section | `true` |
| `REPORT_SECTIONS_ECONOMIC` | Include economic section | `true` |
| `REPORT_SECTIONS_PRODUCTION` | Include production section | `true` |

### Google Sheets Configuration

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable APIs:**
   - Enable Google Sheets API
   - Enable Google Drive API

3. **Create Service Account:**
   - Go to IAM & Admin > Service Accounts
   - Create a new service account
   - Download the JSON credentials file
   - Place it in `cred/google_credentials.json`

4. **Configure Spreadsheet:**
   - Create a new Google Spreadsheet or use existing one
   - Share it with your service account email
   - Copy the spreadsheet ID to `GOOGLE_SHEETS_EXISTING_ID`

## 📝 Monitoring and Logs

### View Logs

```bash
# View all logs
docker-compose logs eclesiar-scheduler

# Follow logs in real-time
docker-compose logs -f eclesiar-scheduler

# View only cron logs
docker-compose exec eclesiar-scheduler tail -f /app/logs/cron.log
```

### Health Check

The container includes a health check that monitors the cron daemon:
```bash
# Check container health
docker-compose ps

# View health status
docker inspect eclesiar-scheduler | grep -A 10 "Health"
```

## 🛠️ Management Commands

### Start/Stop/Restart

```bash
# Start the scheduler
docker-compose up -d

# Stop the scheduler
docker-compose down

# Restart the scheduler
docker-compose restart eclesiar-scheduler

# Rebuild and restart
docker-compose up -d --build
```

### Manual Report Generation

```bash
# Generate report manually
docker-compose exec eclesiar-scheduler python3 main.py google-sheets-report

# Generate different report types
docker-compose exec eclesiar-scheduler python3 main.py daily-report
docker-compose exec eclesiar-scheduler python3 main.py production-analysis
```

### Update Configuration

```bash
# After changing .env file
docker-compose down
docker-compose up -d
```

## 🔍 Troubleshooting

### Common Issues

1. **Google Sheets API Error:**
   - Verify credentials file is in `cred/google_credentials.json`
   - Check service account has access to the spreadsheet
   - Ensure APIs are enabled in Google Cloud Console

2. **API Authentication Error:**
   - Verify `AUTH_TOKEN` in `.env` file
   - Check API token is valid and has required permissions

3. **Cron Not Running:**
   - Check container logs: `docker-compose logs eclesiar-scheduler`
   - Verify cron daemon is running: `docker-compose exec eclesiar-scheduler service cron status`

4. **Permission Issues:**
   - Ensure volume directories exist and have proper permissions
   - Check file ownership in mounted volumes

### Debug Mode

```bash
# Run container in interactive mode for debugging
docker-compose run --rm eclesiar-scheduler bash

# Inside container, test manually:
python3 main.py google-sheets-report
```

## 📈 Scaling and Production

### Resource Limits

The container is configured with resource limits:
- Memory: 512MB limit, 256MB reservation
- CPU: 0.5 cores limit, 0.25 cores reservation

### Production Considerations

1. **Backup Strategy:**
   - Regular backups of `data/` directory
   - Backup of Google Sheets credentials

2. **Monitoring:**
   - Set up log monitoring for cron.log
   - Monitor Google Sheets API quotas
   - Track container health and resource usage

3. **Security:**
   - Keep credentials secure
   - Regularly rotate API tokens
   - Use Docker secrets for sensitive data (production)

## 🆘 Support

For issues or questions:
1. Check the logs first: `docker-compose logs eclesiar-scheduler`
2. Verify configuration in `.env` file
3. Test manual execution: `docker-compose exec eclesiar-scheduler python3 main.py google-sheets-report`
4. Check Google Sheets API quotas and permissions

---

**Copyright (c) 2025 Teo693**  
**Licensed under the MIT License**
