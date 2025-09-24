# Application Behavior After `docker-compose up -d`

## 🚀 What Happens When You Run `docker-compose up -d`

### 1. Container Startup Process

1. **Build Phase**:
   - Builds Docker image from Dockerfile
   - Installs system dependencies (cron, curl, procps)
   - Installs Python dependencies from `requirements/docker.txt` (optimized for Docker)
   - Copies application code to `/app/`
   - Creates necessary directories (`/app/logs`, `/app/reports`, `/app/data`, `/app/cred`)

2. **Cron Job Setup**:
   - Creates cron job: `0 */3 * * * root cd /app && /usr/local/bin/python3 main.py google-sheets-report --economic-only`
   - This runs every 3 hours and generates Google Sheets reports with economic and production sections

3. **Startup Script Execution**:
   - Starts cron daemon
   - Shows cron configuration for debugging
   - **Runs initial data initialization**: `src/cli/docker_init_data.py`
   - Keeps container running and shows logs

### 2. Initial Data Initialization (`docker_init_data.py`)

The startup script runs the following sequence:

1. **Database Initialization**:
   - Initializes database manager
   - Updates database with fresh data from API
   - Fetches countries, currencies, regions, jobs, market data

2. **Historical Data Creation**:
   - Creates initial historical data entry for baseline comparisons
   - Saves current currency rates as baseline for future comparisons

3. **Initial Report Generation**:
   - Generates initial Google Sheets report with economic and production sections
   - Uses same sections as cron job: `economic: True, production: True`

### 3. Ongoing Operation

1. **Cron Job (Every 3 Hours)**:
   - Runs: `main.py google-sheets-report --economic-only`
   - Generates Google Sheets reports with economic and production sections
   - Logs output to `/app/logs/cron.log`

2. **Container Health**:
   - Health check monitors cron process
   - Container restarts automatically if it fails
   - Logs are available via `docker logs eclesiar-scheduler`

## 📊 Report Sections

### Economic-Only Reports (Cron + Initial)
- ✅ **Economic Section**: Currency rates, job offers, market data
- ✅ **Production Section**: Regional productivity analysis
- ❌ **Military Section**: War statistics (excluded)
- ❌ **Warriors Section**: Heroes ranking (excluded)

### Full Reports (Manual)
- ✅ **All Sections**: Military, Warriors, Economic, Production

## 🔧 Key Features

1. **Automatic Data Updates**: Database refreshed every 3 hours
2. **Historical Data Building**: Baseline data created on first run
3. **Google Sheets Integration**: Reports automatically uploaded to Google Sheets
4. **Error Handling**: Graceful fallbacks for missing data
5. **Logging**: Comprehensive logging for debugging

## 📁 Data Persistence

Volume mounts ensure data persists between container restarts:
- `./data:/app/data` - Database and cache files
- `./logs:/app/logs` - Application logs
- `./reports:/app/reports` - Generated reports
- `./cred:/app/cred` - Google credentials

## 🎯 Expected Behavior

### First Run (Day 1)
- ✅ Database initialized with fresh data
- ✅ Initial historical data created
- ✅ First Google Sheets report generated
- ✅ Cron job scheduled for every 3 hours
- ⚠️ Some data may show "—" (normal for first run)

### After 24 Hours (Day 2+)
- ✅ Historical comparisons available
- ✅ Change percentages calculated
- ✅ 5-day averages computed
- ✅ Meaningful alerts generated
- ✅ All data fully populated

## 🔍 Monitoring

### Check Container Status
```bash
docker ps
```

### View Logs
```bash
docker logs eclesiar-scheduler
```

### Check Cron Logs
```bash
docker exec -it eclesiar-scheduler tail -f /app/logs/cron.log
```

### Debug Data Issues
```bash
docker exec -it eclesiar-scheduler python3 src/cli/debug_data_issues.py
```

## 🚨 Troubleshooting

### If Reports Show "—" or "No data available"
1. Check if database has data: `debug_data_issues.py`
2. Verify API connectivity
3. Check Google Sheets credentials
4. Wait 24 hours for historical data to build

### If Container Fails to Start
1. Check environment variables in `.env`
2. Verify Google credentials file exists
3. Check container logs for errors
4. Ensure required directories exist

## ✅ Success Indicators

- Container runs without errors
- Cron job executes every 3 hours
- Google Sheets reports are generated
- Database contains fresh data
- Logs show successful operations
