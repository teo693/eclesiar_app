# Docker Data Issues - Fixes and Solutions

## 🔍 Problem Analysis

The Google Sheets reports in Docker environment show "—" and "No production data available" because:

1. **Historical Data Missing**: New Docker containers don't have historical currency rate data
2. **Empty Database**: Fresh containers start with empty databases
3. **Missing avg5_in_gold**: Market data lacks 5-day averages
4. **No Baseline Data**: First run has no comparison data

## 🛠️ Applied Fixes

### 1. Enhanced Data Fallbacks

**File**: `src/reports/exporters/enhanced_sheets_formatter.py`

- **Currency Analysis**: Added fallback to use current rates as baseline when historical data is missing
- **Market Data**: Added fallback for missing `avg5_in_gold` data
- **Region Data**: Enhanced error messages with troubleshooting hints
- **Alerts**: Reduced thresholds for first-run scenarios

### 2. Docker Initialization Script

**File**: `src/cli/docker_init_data.py`

- Automatically initializes database with fresh data
- Creates initial historical data entry
- Generates baseline Google Sheets report
- Waits for API connectivity before proceeding

### 3. Debug Script

**File**: `src/cli/debug_data_issues.py`

- Comprehensive diagnostics for data issues
- Database connectivity testing
- API connectivity verification
- Google Sheets configuration validation

### 4. Enhanced Error Messages

- Added informative messages when data is missing
- Included troubleshooting hints in Google Sheets
- Better debugging information for Docker environment

## 🚀 Usage Instructions

### For New Docker Deployments

1. **Build and start the container**:
   ```bash
   docker-compose up --build
   ```

2. **The container will automatically**:
   - Initialize the database
   - Fetch fresh data from API
   - Create baseline historical data
   - Generate initial Google Sheets report

### For Existing Docker Deployments

1. **Run the debug script**:
   ```bash
   docker exec -it eclesiar-scheduler python3 src/cli/debug_data_issues.py
   ```

2. **Manually initialize data**:
   ```bash
   docker exec -it eclesiar-scheduler python3 src/cli/docker_init_data.py
   ```

3. **Update database manually**:
   ```bash
   docker exec -it eclesiar-scheduler python3 main.py update-database
   ```

## 🔧 Troubleshooting

### Problem: "No production data available"

**Solution**:
```bash
# Check if database has data
docker exec -it eclesiar-scheduler python3 src/cli/debug_data_issues.py

# If empty, update database
docker exec -it eclesiar-scheduler python3 main.py update-database
```

### Problem: "Previous Rate —" and "Change % —"

**Solution**:
```bash
# This is normal for first run
# Historical data will be available after 24 hours
# Or manually create baseline:
docker exec -it eclesiar-scheduler python3 src/cli/docker_init_data.py
```

### Problem: "Stock —" and "5-Day Avg —"

**Solution**:
```bash
# Update market data
docker exec -it eclesiar-scheduler python3 main.py update-database

# Check if market offers are being fetched
docker exec -it eclesiar-scheduler python3 src/cli/debug_data_issues.py
```

### Problem: "No active alerts"

**Solution**:
- This is normal for first run
- Alerts will appear after baseline data is established
- Check again after 24 hours of operation

## 📊 Expected Behavior

### First Run (Day 1)
- ✅ Currency rates will show current values
- ✅ Previous Rate will show "—" (normal)
- ✅ Change % will show "—" (normal)
- ✅ Stock data will show current prices
- ✅ 5-Day Avg will show "—" (normal)
- ✅ Region data will show if database is populated
- ✅ Alerts will be minimal or show "First Run" message

### After 24 Hours (Day 2+)
- ✅ Previous Rate will show yesterday's values
- ✅ Change % will show actual percentage changes
- ✅ 5-Day Avg will show calculated averages
- ✅ Alerts will show meaningful opportunities
- ✅ All data will be fully populated

## 🔄 Automatic Data Collection

The Docker container is configured to:
- Update database every 3 hours via cron
- Generate Google Sheets reports every 3 hours
- Build historical data over time
- Maintain data freshness automatically

## 📝 Monitoring

Check container logs:
```bash
docker logs eclesiar-scheduler
```

Check cron logs:
```bash
docker exec -it eclesiar-scheduler tail -f /app/logs/cron.log
```

## 🎯 Key Improvements

1. **Graceful Degradation**: App works even with missing data
2. **Informative Messages**: Users understand what's happening
3. **Automatic Initialization**: Docker containers self-configure
4. **Better Fallbacks**: Missing data doesn't break reports
5. **Enhanced Debugging**: Easy troubleshooting tools

## 📞 Support

If issues persist:
1. Run `src/cli/debug_data_issues.py` for detailed diagnostics
2. Check API connectivity and authentication
3. Verify Google Sheets credentials
4. Ensure database permissions are correct
