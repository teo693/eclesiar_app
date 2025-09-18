# 🔧 Troubleshooting Guide

## Overview

This comprehensive troubleshooting guide covers common issues, solutions, and debugging techniques for the Eclesiar application. Use this guide to quickly resolve problems and understand the application's behavior.

## 🚨 Common Issues

### 1. Installation & Dependencies

#### Python Version Issues
**Problem**: Application fails to start or import errors
```
ImportError: No module named 'src'
SyntaxError: f-strings are only supported in Python 3.6+
```

**Solution**:
```bash
# Check Python version (requires 3.6+)
python3 --version

# Use correct Python version
python3 -m pip install -r requirements/base.txt
python3 main.py
```

#### Missing Dependencies
**Problem**: Module import errors
```
ModuleNotFoundError: No module named 'docx'
ModuleNotFoundError: No module named 'requests'
```

**Solution**:
```bash
# Install all dependencies
pip install -r requirements/base.txt

# Install specific missing packages
pip install python-docx requests sqlite3
```

#### Virtual Environment Issues
**Problem**: Conflicts with system packages

**Solution**:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies in virtual environment
pip install -r requirements/base.txt
```

### 2. Configuration Issues

#### Missing Environment File
**Problem**: Application can't find configuration
```
FileNotFoundError: .env file not found
KeyError: 'AUTH_TOKEN'
```

**Solution**:
```bash
# Copy example configuration
cp .env.example .env

# Edit with your API credentials
nano .env
```

#### Invalid API Credentials
**Problem**: Authentication failures
```
401 Unauthorized
403 Forbidden
Invalid API key format
```

**Solution**:
1. **Check API key format**:
   ```bash
   # Correct format: eclesiar_prod_YOUR_KEY
   AUTH_TOKEN="eclesiar_prod_abc123def456"
   ```

2. **Test API connection**:
   ```bash
   curl -H "Authorization: Bearer eclesiar_prod_YOUR_KEY" \
        https://api.eclesiar.com/countries
   ```

3. **Verify key hasn't expired**:
   - Contact Eclesiar administration
   - Check game account status

#### Database Path Issues
**Problem**: Database access errors
```
sqlite3.OperationalError: unable to open database file
PermissionError: [Errno 13] Permission denied: 'data/eclesiar.db'
```

**Solution**:
```bash
# Create data directory
mkdir -p data

# Check permissions
ls -la data/
chmod 755 data/
chmod 644 data/eclesiar.db  # if file exists

# Set custom database path
export ECLESIAR_DB_PATH="/path/to/your/database.db"
```

### 3. Database Issues

#### Database Corruption
**Problem**: SQLite database corruption
```
sqlite3.DatabaseError: database disk image is malformed
sqlite3.OperationalError: database is locked
```

**Solution**:
```bash
# Backup current database
cp data/eclesiar.db data/eclesiar.db.backup

# Try to repair
sqlite3 data/eclesiar.db ".dump" | sqlite3 data/eclesiar_repaired.db
mv data/eclesiar_repaired.db data/eclesiar.db

# If repair fails, start fresh
rm data/eclesiar.db
python3 main.py  # Will create new database
```

#### Migration Errors
**Problem**: Database schema migration failures
```
sqlite3.OperationalError: no such column: bonus_by_type
sqlite3.OperationalError: table already exists
```

**Solution**:
1. **Check current schema**:
   ```bash
   sqlite3 data/eclesiar.db ".schema regions_data"
   ```

2. **Manual migration**:
   ```sql
   ALTER TABLE regions_data ADD COLUMN bonus_by_type TEXT DEFAULT '{}';
   ```

3. **Reset database if needed**:
   ```bash
   rm data/eclesiar.db
   python3 -c "from src.data.database.models import init_db; init_db()"
   ```

#### Performance Issues
**Problem**: Slow database operations
```
Database operations taking too long
High CPU usage during data loading
```

**Solution**:
```bash
# Optimize database
sqlite3 data/eclesiar.db "VACUUM;"
sqlite3 data/eclesiar.db "ANALYZE;"

# Add indexes for common queries
sqlite3 data/eclesiar.db "CREATE INDEX IF NOT EXISTS idx_item_prices_ts ON item_prices(ts);"
sqlite3 data/eclesiar.db "CREATE INDEX IF NOT EXISTS idx_currency_rates_ts ON currency_rates(ts);"
```

### 4. API Issues

#### Network Connectivity
**Problem**: Can't reach Eclesiar API
```
requests.exceptions.ConnectionError
requests.exceptions.Timeout
DNS resolution failed
```

**Solution**:
```bash
# Test basic connectivity
ping api.eclesiar.com
curl -I https://api.eclesiar.com

# Check proxy settings
echo $http_proxy
echo $https_proxy

# Test with different timeout
export API_TIMEOUT=30
```

#### Rate Limiting
**Problem**: Too many API requests
```
429 Too Many Requests
Rate limit exceeded
```

**Solution**:
1. **Reduce concurrent workers**:
   ```bash
   # In .env file
   API_WORKERS_MARKET=2
   API_WORKERS_REGIONS=3
   API_WORKERS_WAR=2
   ```

2. **Add delays between requests**:
   ```python
   # In API client
   time.sleep(0.1)  # 100ms delay
   ```

#### Data Format Changes
**Problem**: API response format changed
```
KeyError: 'expected_field'
TypeError: expected dict, got list
```

**Solution**:
1. **Check API response**:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        https://api.eclesiar.com/countries | jq .
   ```

2. **Update data parsing**:
   - Check `src/data/api/client.py`
   - Update field mappings
   - Handle missing fields gracefully

### 5. Report Generation Issues

#### Missing Data
**Problem**: Reports contain no data or errors
```
No military data available
No economic data found
Empty report generated
```

**Solution**:
1. **Check data freshness**:
   ```bash
   # Force database update
   python3 main.py --force-refresh
   ```

2. **Verify sections configuration**:
   ```python
   sections = {
       'military': True,
       'warriors': True, 
       'economic': True,
       'production': True
   }
   ```

3. **Check individual data sources**:
   ```python
   from src.core.services.database_manager_service import DatabaseManagerService
   db = DatabaseManagerService()
   print(db.get_countries_data())
   ```

#### File Permission Errors
**Problem**: Can't write report files
```
PermissionError: [Errno 13] Permission denied: 'reports/daily_report.docx'
FileNotFoundError: [Errno 2] No such file or directory: 'reports'
```

**Solution**:
```bash
# Create reports directory
mkdir -p reports

# Check permissions
ls -la reports/
chmod 755 reports/

# Use custom output directory
python3 main.py daily-report --output-dir /tmp/reports
```

#### Encoding Issues
**Problem**: Unicode/encoding errors in reports
```
UnicodeEncodeError: 'ascii' codec can't encode character
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**Solution**:
```bash
# Set proper locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Use UTF-8 encoding in Python
export PYTHONIOENCODING=utf-8
```

### 6. Docker Issues

#### Container Won't Start
**Problem**: Docker container fails to start
```
docker: Error response from daemon
Container exits immediately
Permission denied in container
```

**Solution**:
```bash
# Check Docker daemon
sudo systemctl status docker
sudo systemctl start docker

# Check container logs
docker logs eclesiar-scheduler

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Volume Mount Issues
**Problem**: Data not persisting or accessible
```
Volume mount failed
Data directory empty in container
Permission denied on mounted volume
```

**Solution**:
```bash
# Check volume mounts
docker-compose config

# Fix permissions
sudo chown -R $USER:$USER data/
sudo chmod -R 755 data/

# Recreate volumes
docker-compose down -v
docker-compose up -d
```

#### Environment Variables
**Problem**: Environment variables not working in Docker
```
Environment variable not found
Configuration not loading properly
```

**Solution**:
```bash
# Check environment file
ls -la .env
cat .env

# Verify Docker Compose configuration
docker-compose config

# Pass environment explicitly
docker run -e AUTH_TOKEN="your_token" eclesiar-app
```

## 🔍 Debugging Techniques

### 1. Enable Debug Logging

```bash
# Set debug log level
export LOG_LEVEL=DEBUG

# Enable verbose output
python3 main.py --verbose
```

### 2. Check Application Logs

```bash
# View recent logs
tail -f logs/eclesiar.log

# Search for specific errors
grep "ERROR" logs/eclesiar.log
grep "Exception" logs/eclesiar.log
```

### 3. Database Inspection

```bash
# Connect to database
sqlite3 data/eclesiar.db

# Check table contents
.tables
SELECT COUNT(*) FROM countries;
SELECT * FROM countries LIMIT 5;

# Check recent data
SELECT created_at FROM api_snapshots ORDER BY created_at DESC LIMIT 1;
```

### 4. API Testing

```bash
# Test authentication
curl -H "Authorization: Bearer $AUTH_TOKEN" \
     https://api.eclesiar.com/countries

# Test specific endpoints
curl -H "Authorization: Bearer $AUTH_TOKEN" \
     https://api.eclesiar.com/market/items

# Save response for analysis
curl -H "Authorization: Bearer $AUTH_TOKEN" \
     https://api.eclesiar.com/countries > api_response.json
```

### 5. Python Debugging

```python
# Add debug prints
print(f"Data: {data}")
print(f"Type: {type(data)}")

# Use Python debugger
import pdb; pdb.set_trace()

# Check variable values
import json
print(json.dumps(data, indent=2))
```

## 📊 Performance Monitoring

### 1. Resource Usage

```bash
# Monitor system resources
top -p $(pgrep -f eclesiar)
htop

# Check disk usage
du -sh data/
df -h

# Monitor memory usage
ps aux | grep python
```

### 2. Database Performance

```bash
# Check database size
ls -lh data/eclesiar.db

# Monitor query performance
sqlite3 data/eclesiar.db "EXPLAIN QUERY PLAN SELECT * FROM countries;"

# Check table sizes
sqlite3 data/eclesiar.db "SELECT name, COUNT(*) FROM sqlite_master WHERE type='table' GROUP BY name;"
```

### 3. API Performance

```bash
# Measure API response times
time curl -H "Authorization: Bearer $AUTH_TOKEN" \
          https://api.eclesiar.com/countries

# Monitor network usage
netstat -i
iftop
```

## 🛡️ Security Considerations

### 1. API Key Security

```bash
# Never commit API keys
git status
git diff

# Check for accidental commits
git log --grep="token\|key\|password" --oneline

# Use environment variables only
grep -r "eclesiar_prod" . --exclude-dir=.git
```

### 2. File Permissions

```bash
# Secure configuration files
chmod 600 .env
chmod 600 cred/google_credentials.json

# Check for world-readable files
find . -type f -perm /o+r
```

### 3. Data Protection

```bash
# Backup sensitive data
cp data/eclesiar.db backups/eclesiar_$(date +%Y%m%d).db

# Encrypt backups
gpg -c backups/eclesiar_20250918.db
```

## 📞 Support Resources

### 1. Application Logs
- **Location**: `logs/eclesiar.log`
- **Rotation**: Daily rotation
- **Levels**: DEBUG, INFO, WARNING, ERROR

### 2. Database Tools
- **SQLite Browser**: GUI for database inspection
- **Command Line**: `sqlite3` for direct access
- **Backup Scripts**: Automated backup solutions

### 3. Development Tools
- **IDE**: VS Code with Python extension
- **Debugger**: Python's built-in `pdb`
- **Profiler**: `cProfile` for performance analysis

### 4. Community Support
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive guides in `docs/`
- **Examples**: Sample configurations and scripts

## 🔄 Recovery Procedures

### 1. Complete Reset

```bash
# Backup current state
tar -czf backup_$(date +%Y%m%d).tar.gz data/ logs/ reports/

# Clean everything
rm -rf data/ logs/ reports/
rm .env

# Restore from templates
cp .env.example .env
# Edit .env with your credentials

# Reinitialize
python3 main.py
```

### 2. Partial Recovery

```bash
# Keep database, reset configuration
cp .env.example .env.new
# Edit .env.new and replace .env

# Keep configuration, reset database
rm data/eclesiar.db
python3 main.py  # Will recreate database
```

### 3. Docker Recovery

```bash
# Complete Docker reset
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

---

**Troubleshooting Guide Version**: 3.3  
**Last Updated**: 2025-09-18  
**Language**: English  

**Copyright (c) 2025 Teo693**  
**Licensed under the MIT License**

For additional support, please check the main [README.md](../README.md) or create an issue on GitHub.
