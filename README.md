# Eclesiar - Game Data Analysis Application

Comprehensive application for analyzing data from the Eclesiar game, featuring daily reports, regional productivity analysis, currency arbitrage analysis, and interactive production calculators.

## 🏗️ Project Structure

```
eclesiar_app/
├── main.py                           # Main entry point with interactive menu
├── src/                              # Source code
│   ├── core/                         # Business logic
│   │   ├── services/                 # Business services
│   │   │   ├── orchestrator_service.py      # Main application orchestrator
│   │   │   ├── economy_service.py           # Economic functions
│   │   │   ├── military_service.py          # Military functions
│   │   │   ├── regions_service.py           # Regional functions
│   │   │   ├── calculator_service.py        # Interactive production calculator
│   │   │   └── quick_calculator_service.py  # Quick production calculator
│   │   ├── models/                   # Data models
│   │   └── utils/                    # Utility functions
│   ├── data/                         # Data layer
│   │   ├── api/                      # API client
│   │   │   └── client.py             # API client implementation
│   │   ├── database/                 # Database layer
│   │   │   └── models.py             # SQLite database models
│   │   └── storage/                  # Data management
│   │       └── cache.py              # Cache and storage management
│   ├── reports/                      # Report generation
│   │   ├── generators/               # Report generators
│   │   │   ├── daily_report.py       # Daily report generation
│   │   │   ├── html_report.py        # HTML report generation
│   │   │   ├── production_report.py  # Regional productivity analysis
│   │   │   ├── arbitrage_report.py   # Currency arbitrage analysis
│   │   │   └── short_economic_report.py # Short economic report generator
│   │   ├── templates/                # Report templates
│   │   └── exporters/                # Export to different formats
│   │       ├── export_markdown.py    # Markdown export
│   │       ├── export_plaintext.py   # Plain text export
│   │       ├── export_rtf.py         # RTF export
│   │       └── export_all_formats.py # All formats export
│   └── cli/                          # Command line interface
│       └── web_api.py                # Web API interface
├── config/                           # Configuration
│   ├── settings/                     # Application settings
│   │   ├── base.py                   # Base configuration
│   │   └── production.py             # Production configuration
│   └── environments/                 # Environment configurations
├── docs/                             # Documentation
│   ├── api/                          # API documentation
│   ├── user/                         # User documentation
│   └── development/                  # Development documentation
├── tests/                            # Tests
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── fixtures/                     # Test data
├── data/                             # Data files
│   ├── eclesiar.db                   # SQLite database
│   └── historia_raportow.json        # Report history
├── logs/                             # Application logs
├── requirements/                     # Dependencies
│   └── base.txt                      # Base dependencies
├── .env.example                      # Environment configuration example
├── .gitignore                        # Git ignore file
├── pyproject.toml                    # Project configuration
└── README.md                         # This file
```

## 🚀 Getting Started

### Install dependencies
```bash
pip install -r requirements/base.txt
```

### Environment setup
```bash
# Copy environment configuration
cp .env.example .env

# Edit .env file with your API credentials
nano .env
```

### Running the application

#### Interactive Mode (Recommended)
```bash
python main.py
```
This launches the interactive menu where you can select from all available options.

#### Command Line Mode

##### 1. Generate daily report
```bash
python main.py daily-report
```

##### 2. Regional productivity analysis
```bash
python main.py production-analysis
```

##### 3. Currency arbitrage analysis
```bash
python main.py arbitrage-analysis --min-profit 1.0
```

##### 4. Short economic report (DOCX)
```bash
python main.py short-economic-report
```

##### 5. Full analysis (all modules)
```bash
python main.py full-analysis
```

##### 6. Interactive Production Calculator
```bash
python main.py production-calculator
```

##### 7. Quick Production Calculator (Test scenarios)
```bash
python main.py quick-calculator
```

### Additional options
```bash
python main.py daily-report --output-dir custom_reports
python main.py arbitrage-analysis --min-profit 2.0 --output-dir arbitrage_results
```

## 📊 Features

### 📋 Daily Reports
- Military statistics (wars, damage)
- Top warriors ranking
- Economic analysis (currency rates, job offers)
- Comparisons with previous days
- DOCX format generation

### 🏭 Regional Productivity Analysis
- Production efficiency calculations
- Regional and national bonuses consideration
- Pollution and NPC wages analysis
- Regional ranking by efficiency score

### 💰 Currency Arbitrage Analysis
- Arbitrage opportunity detection
- Transaction risk analysis
- Market liquidity assessment
- CSV and TXT report generation
- Strategy backtesting

### 📈 Short Economic Report
- All currency rates vs GOLD
- Cheapest item of each type from all countries
- Best production region for each product
- Compact DOCX format for quick reference

### 🧮 Production Calculator
- **Interactive Calculator**: Full-featured calculator with region selection, company parameters, and detailed analysis
- **Quick Calculator**: Fast testing of different scenarios with predefined parameters
- **Real-time Calculations**: All 8 production factors from Eclesiar documentation
- **Parameter Configuration**: Company tier, eco skill, workers, building levels, military base, ownership type
- **Efficiency Analysis**: Detailed scoring and recommendations for optimization
- **Multiple Products**: Support for all production types (weapon, iron, grain, aircraft, etc.)

## ⚙️ Configuration

### .env file
```env
# API Configuration
API_URL=https://api.eclesiar.com
AUTH_TOKEN=your_token_here
ECLESIAR_API_KEY=your_api_key_here

# Database
DATABASE_PATH=data/eclesiar.db

# Workers
API_WORKERS_MARKET=6
API_WORKERS_REGIONS=8
API_WORKERS_WAR=4
API_WORKERS_HITS=4

# Cache
CACHE_TTL_MINUTES=5
USE_CACHE=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/eclesiar.log

# Arbitrage Configuration
TICKET_COST_GOLD=0.1
MIN_PROFIT_THRESHOLD=0.5
MIN_SPREAD_THRESHOLD=0.001
```

### Configuration files
- **Base configuration**: `config/settings/base.py` - Main application settings
- **Production configuration**: `config/settings/production.py` - Production-specific settings
- **Project configuration**: `pyproject.toml` - Python project metadata and dependencies

## 📁 Report Organization

### Daily reports
- **Location**: `reports/`
- **Formats**: DOCX, HTML
- **Naming**: `raport_dzienny_YYYY-MM-DD_HH-MM.docx`

### Productivity analysis
- **Location**: `reports/`
- **Formats**: TXT
- **Naming**: `production_analysis_YYYYMMDD_HHMMSS.txt`

### Arbitrage reports
- **Location**: `reports/`
- **Formats**: CSV, TXT
- **Naming**: `arbitrage_report_YYYYMMDD_HHMMSS.csv`

### Short economic reports
- **Location**: `reports/`
- **Formats**: DOCX
- **Naming**: `skrocony_raport_ekonomiczny_YYYY-MM-DD_HH-MM.docx`

## 📚 Documentation

### User Documentation
- **Installation**: `docs/user/installation.md` - Setup instructions
- **Calculator**: `docs/user/calculator.md` - Production calculator guide
- **Arbitrage**: `docs/user/arbitrage.md` - Arbitrage analysis guide

### API Documentation
- **API Guide**: `docs/api/README.md` - API usage guide
- **Troubleshooting**: `docs/api/troubleshooting.md` - Common issues and solutions

### Development Documentation
- **Refactoring Plan**: `docs/development/refactoring_plan.md` - Project refactoring roadmap
- **Security**: `docs/development/security.md` - Security considerations
- **Production Analysis**: `docs/development/production_analysis.md` - Production analysis details

## 🔧 Development

### Project Structure
The project follows a clean architecture pattern with clear separation of concerns:

- **`src/core/`** - Business logic and domain models
- **`src/data/`** - Data access layer (API, database, storage)
- **`src/reports/`** - Report generation and export functionality
- **`src/cli/`** - Command line interface components
- **`config/`** - Configuration management
- **`tests/`** - Test suites (unit, integration, fixtures)

### Adding new modules
1. Create new Python file in appropriate directory under `src/`
2. Add import in `main.py` or relevant service
3. Add new command in argument parser if needed
4. Update documentation in `docs/`
5. Add tests in `tests/`

### Testing
```bash
# Test single module
python3 -c "from src.reports.generators.production_report import ProductionAnalyzer; print('OK')"

# Test full application
python3 main.py full-analysis

# Run tests (when implemented)
pytest tests/
```

### Development setup
```bash
# Install development dependencies
pip install -r requirements/base.txt

# Install development tools
pip install black flake8 mypy pytest

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 📝 Changelog

### v3.0 - Major Refactoring (2025-01-09) 🚀
- ✅ **Complete project reorganization** - Implemented clean architecture
- ✅ **New project structure** - Separated concerns into logical layers
- ✅ **30 Python files reorganized** - Moved to appropriate directories
- ✅ **Updated all imports** - Fixed import paths throughout the project
- ✅ **Removed backup files** - Cleaned up duplicate and backup files
- ✅ **Added configuration management** - Centralized config in `config/` directory
- ✅ **Enhanced documentation** - Organized docs into user/API/development sections
- ✅ **Added project metadata** - `pyproject.toml` for modern Python packaging
- ✅ **Environment configuration** - `.env.example` for easy setup
- ✅ **Git configuration** - Comprehensive `.gitignore` file
- ✅ **Package structure** - Added `__init__.py` files for proper Python packages
- ✅ **Tested functionality** - Verified all imports and basic functionality work

### v2.3 - Production Calculator (2025-09-08)
- ✅ Added interactive production calculator with full parameter configuration
- ✅ Added quick production calculator for testing scenarios
- ✅ Implemented all 8 production factors from Eclesiar documentation
- ✅ Added region selection with real-time data from API
- ✅ Integrated calculators with main application menu
- ✅ Added new commands: `python main.py production-calculator` and `python main.py quick-calculator`
- ✅ Created comprehensive calculator documentation (CALCULATOR_README.md)
- ✅ Translated all application interfaces to English

### v2.2 - Short Economic Report (2025-09-08)
- ✅ Added short economic report generation (DOCX)
- ✅ Includes all currency rates vs GOLD
- ✅ Shows cheapest item of each type from all countries
- ✅ Displays best production region for each product
- ✅ Integrated with main application menu and CLI
- ✅ Added new command: `python main.py short-economic-report`

### v2.1 - English Translation (2025-09-08)
- ✅ Added NPC wages column to productivity table
- ✅ Translated entire application to English
- ✅ Fixed military sections appearing in economic reports
- ✅ Updated README to English
- ✅ Translated console menu and all output messages

### v2.0 - Reorganization (2025-09-03)
- ✅ Removed duplicate files
- ✅ Consolidated production and arbitrage analyzers
- ✅ Organized reports in separate folders
- ✅ Created main entry point (`main.py`)
- ✅ Organized project structure
- ✅ Updated documentation

### v1.0 - Initial version
- Basic reporting functionality
- Regional productivity analysis
- Currency arbitrage analysis

## 🤝 Support

In case of problems or questions:
1. Check application logs
2. Make sure all dependencies are installed
3. Check API configuration in `.env` file
4. Check write permissions in output directories

## 📄 License

Private project - for internal use only.
