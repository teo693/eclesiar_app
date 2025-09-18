# 📦 Eclesiar Application Installation Guide

## Overview

Complete installation and setup guide for the Eclesiar game data analysis application. This guide covers everything from initial setup to advanced configuration options.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Docker Setup](#docker-setup)
- [Troubleshooting](#troubleshooting)
- [Feature Overview](#feature-overview)

## 💻 System Requirements

### Minimum Requirements
- **Python**: 3.6 or higher
- **Operating System**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **RAM**: 512 MB available
- **Storage**: 100 MB free space
- **Network**: Internet connection for API access

### Recommended Requirements
- **Python**: 3.8 or higher
- **RAM**: 1 GB available
- **Storage**: 1 GB free space (for data storage and reports)
- **Network**: Stable broadband connection

### Dependencies
All dependencies are automatically installed via `requirements/base.txt`:
- `requests` - HTTP client for API communication
- `python-docx` - DOCX report generation
- `sqlite3` - Database operations (included with Python)
- `concurrent.futures` - Parallel processing (included with Python)

## 🚀 Quick Start

### 1. Download and Extract
```bash
# Clone from repository
git clone https://github.com/yourusername/eclesiar_app.git
cd eclesiar_app

# Or extract from ZIP file
unzip eclesiar_app.zip
cd eclesiar_app
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements/base.txt

# For virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements/base.txt
```

### 3. Configure API Access
```bash
# Copy configuration template
cp .env.example .env

# Edit configuration file
nano .env  # Linux/Mac
# or
notepad .env  # Windows
```

### 4. Set Your API Key
```bash
# In .env file, replace YOUR_API_KEY_HERE with your actual key
AUTH_TOKEN="eclesiar_prod_YOUR_ACTUAL_API_KEY"
```

### 5. Test Installation
```bash
# Run application in interactive mode
python3 main.py

# Test API connection
curl -H "Authorization: Bearer eclesiar_prod_YOUR_KEY" \
     https://api.eclesiar.com/countries
```

## 🔧 Detailed Installation

### Virtual Environment Setup (Recommended)

#### Why Use Virtual Environment?
- Isolates project dependencies
- Prevents conflicts with system packages
- Easier dependency management
- Clean uninstallation

#### Setup Instructions
```bash
# Create virtual environment
python3 -m venv eclesiar_env

# Activate virtual environment
source eclesiar_env/bin/activate  # Linux/Mac
# or
eclesiar_env\Scripts\activate     # Windows

# Verify activation (should show virtual env path)
which python

# Install dependencies
pip install -r requirements/base.txt

# Deactivate when done
deactivate
```

### System-Wide Installation
```bash
# Install dependencies globally
pip install -r requirements/base.txt

# For older Python versions, use pip3
pip3 install -r requirements/base.txt

# Verify installation
python3 -c "import requests, docx; print('Dependencies installed successfully')"
```

### Development Installation
```bash
# Install development dependencies
pip install -r requirements/base.txt

# Install development tools
pip install black flake8 mypy pytest

# Install in development mode
pip install -e .
```

## ⚙️ Configuration

### Environment Variables

Create and configure your `.env` file:

```bash
# API Configuration
AUTH_TOKEN="eclesiar_prod_YOUR_API_KEY_HERE"
API_URL="https://api.eclesiar.com"
API_TIMEOUT=30

# Database Configuration
ECLESIAR_DB_PATH="data/eclesiar.db"

# Worker Configuration
API_WORKERS_MARKET=6
API_WORKERS_REGIONS=8
API_WORKERS_WAR=4
API_WORKERS_HITS=4

# Cache Configuration
CACHE_TTL_MINUTES=5
USE_CACHE=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/eclesiar.log

# Arbitrage Configuration
TICKET_COST_GOLD=0.1
MIN_PROFIT_THRESHOLD=0.5
MIN_SPREAD_THRESHOLD=0.001

# Google Sheets Configuration (Optional)
GOOGLE_SPREADSHEET_ID="your_spreadsheet_id"
GOOGLE_CREDENTIALS_PATH="cred/google_credentials.json"
```

### Configuration Files

#### Base Configuration (`config/settings/base.py`)
```python
# Default application settings
DATABASE_PATH = "data/eclesiar.db"
REPORTS_DIR = "reports"
LOGS_DIR = "logs"
```

#### Production Configuration (`config/settings/production.py`)
```python
# Production-specific settings
DEBUG = False
LOG_LEVEL = "INFO"
CACHE_ENABLED = True
```

### Directory Structure
The application will create these directories automatically:
```
eclesiar_app/
├── data/           # Database and cached data
├── logs/           # Application logs
├── reports/        # Generated reports
├── cred/           # Credentials (create manually)
└── config/         # Configuration files
```

### Manual Directory Creation
```bash
# Create required directories
mkdir -p data logs reports cred

# Set appropriate permissions
chmod 755 data logs reports
chmod 700 cred  # Restricted access for credentials
```

## 🏃 Running the Application

### Interactive Mode (Recommended)
```bash
python3 main.py
```

This launches an interactive menu with all available options:
- Daily report generation (DOCX/HTML)
- Regional productivity analysis
- Currency arbitrage analysis
- Production calculators
- Database management

### Command Line Mode

#### Basic Reports
```bash
# Generate daily report
python3 main.py daily-report

# Generate HTML daily report
python3 main.py daily-report --format html

# Regional productivity analysis
python3 main.py production-analysis

# Currency arbitrage analysis
python3 main.py arbitrage-analysis --min-profit 1.0

# Short economic report
python3 main.py short-economic-report
```

#### Advanced Features
```bash
# Interactive production calculator
python3 main.py production-calculator

# Quick production calculator (test scenarios)
python3 main.py quick-calculator

# Complete analysis (all modules)
python3 main.py full-analysis

# Google Sheets report
python3 main.py google-sheets-report
```

#### Custom Output
```bash
# Custom output directory
python3 main.py daily-report --output-dir custom_reports

# Specific profit threshold for arbitrage
python3 main.py arbitrage-analysis --min-profit 2.0 --output-dir arbitrage_results

# Force database refresh
python3 main.py daily-report --force-refresh
```

### Scheduled Execution

#### Using Cron (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add scheduled execution (every 6 hours)
0 */6 * * * cd /path/to/eclesiar_app && python3 main.py google-sheets-report

# Daily report at 9 AM
0 9 * * * cd /path/to/eclesiar_app && python3 main.py daily-report
```

#### Using Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Set action to run Python script
5. Configure paths and arguments

## 🐳 Docker Setup

### Quick Docker Start
```bash
# Copy Docker environment template
cp docker.env.template .env

# Edit with your credentials
nano .env

# Place Google credentials (if using Google Sheets)
cp your_credentials.json cred/google_credentials.json

# Start automated reporting
./start-docker.sh
```

### Manual Docker Commands
```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f eclesiar-scheduler

# Stop containers
docker-compose down

# Manual report generation
docker-compose exec eclesiar-scheduler python3 main.py google-sheets-report

# Update containers
docker-compose pull
docker-compose up -d
```

### Docker Configuration
```yaml
# docker-compose.yml (example)
version: '3.8'
services:
  eclesiar-scheduler:
    build: .
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./reports:/app/reports
      - ./cred:/app/cred
    env_file:
      - .env
    restart: unless-stopped
```

## 🔧 Troubleshooting

### Common Installation Issues

#### Python Version Problems
```bash
# Check Python version
python3 --version

# If version is too old
sudo apt update && sudo apt install python3.8  # Ubuntu
brew install python@3.8                        # macOS
```

#### Permission Errors
```bash
# Fix directory permissions
sudo chown -R $USER:$USER eclesiar_app/
chmod -R 755 eclesiar_app/

# For pip install errors
pip install --user -r requirements/base.txt
```

#### Missing Dependencies
```bash
# Update pip
python3 -m pip install --upgrade pip

# Install missing system dependencies (Ubuntu)
sudo apt install python3-dev python3-pip

# For macOS
xcode-select --install
```

### Configuration Issues

#### API Key Problems
```bash
# Test API key format
echo $AUTH_TOKEN  # Should start with "eclesiar_prod_"

# Test API connection
curl -H "Authorization: Bearer $AUTH_TOKEN" \
     https://api.eclesiar.com/countries
```

#### Database Issues
```bash
# Reset database
rm data/eclesiar.db
python3 -c "from src.data.database.models import init_db; init_db()"

# Check database permissions
ls -la data/
chmod 644 data/eclesiar.db
```

#### File Not Found Errors
```bash
# Verify working directory
pwd
ls -la

# Create missing directories
mkdir -p data logs reports cred
```

### Performance Issues

#### Slow API Responses
```bash
# Reduce concurrent workers in .env
API_WORKERS_MARKET=3
API_WORKERS_REGIONS=4
API_WORKERS_WAR=2

# Increase timeout
API_TIMEOUT=60
```

#### Large Database Size
```bash
# Optimize database
sqlite3 data/eclesiar.db "VACUUM;"
sqlite3 data/eclesiar.db "ANALYZE;"

# Clean old data
python3 -c "
from src.data.database.models import cleanup_old_data
cleanup_old_data(days=30)
"
```

## 🎯 Feature Overview

### 📊 Daily Reports
- **DOCX Format**: Professional document format
- **HTML Format**: Web-friendly format
- **Military Statistics**: Wars, battles, damage analysis
- **Economic Data**: Currency rates, job offers, market prices
- **Historical Comparison**: Trends and changes over time

### 🏭 Regional Productivity Analysis
- **8 Production Factors**: Complete calculation system
- **Regional Bonuses**: Location-specific production benefits
- **Country Bonuses**: Dynamic calculation based on regional data
- **Efficiency Scoring**: Ranking system for optimal locations
- **Pollution Impact**: Environmental factors consideration

### 💰 Currency Arbitrage Analysis
- **Opportunity Detection**: Automatic arbitrage identification
- **Risk Assessment**: Risk scoring for each opportunity
- **Profit Calculation**: Expected returns and transaction costs
- **Market Liquidity**: Analysis of market depth
- **Strategy Backtesting**: Historical performance analysis

### 🧮 Production Calculators
- **Interactive Calculator**: Full-featured with real-time data
- **Quick Calculator**: Fast scenario testing
- **Parameter Configuration**: Company tier, skills, workers, buildings
- **Real-time Updates**: Fresh data from API
- **Country Bonus Integration**: Automatic bonus calculations

### 📈 Short Economic Reports
- **Currency Overview**: All rates vs GOLD
- **Market Analysis**: Cheapest items by category
- **Production Optimization**: Best regions for each product
- **Compact Format**: Quick reference information

### 🐳 Docker Automation
- **Automated Scheduling**: Reports every 6 hours
- **Google Sheets Integration**: Direct upload to spreadsheets
- **Container Health Monitoring**: Automatic restart on failures
- **Persistent Storage**: Data preservation across restarts
- **Production Ready**: Resource limits and error handling

## 🌍 Internationalization

The application is fully internationalized in English:

### User Interface
- All menus, prompts, and messages in English
- Error messages and warnings in English
- Console output and logging in English
- Help text and documentation in English

### Reports
- All generated reports use English terminology
- Currency names and country names in English
- Technical terms and calculations in English
- Export formats support English encoding

### Code Documentation
- All comments and docstrings in English
- Variable names and function names in English
- Configuration options documented in English

## 📞 Support

### Getting Help

1. **Documentation**: Check relevant documentation files
   - [Troubleshooting Guide](../TROUBLESHOOTING.md)
   - [API Documentation](../api/README.md)
   - [Development Guide](../development/)

2. **Logs**: Check application logs for error details
   ```bash
   tail -f logs/eclesiar.log
   grep "ERROR" logs/eclesiar.log
   ```

3. **Configuration**: Verify your configuration
   ```bash
   python3 -c "
   from src.core.config.app_config import AppConfig
   config = AppConfig.from_env()
   print('Configuration loaded successfully')
   "
   ```

4. **Community**: 
   - GitHub Issues for bug reports
   - Discussions for questions and feature requests

### Support Resources

- **Main Documentation**: [README.md](../../README.md)
- **API Troubleshooting**: [docs/api/troubleshooting.md](../api/troubleshooting.md)
- **Development Setup**: [docs/development/](../development/)
- **Docker Guide**: [docs/docker/](../docker/)

---

**Installation Guide Version**: 3.3  
**Last Updated**: 2025-09-18  
**Language**: English  

**Copyright (c) 2025 Teo693**  
**Licensed under the MIT License**