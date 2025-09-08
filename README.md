# Eclesiar - Game Data Analysis Application

Comprehensive application for analyzing data from the Eclesiar game, featuring daily reports, regional productivity analysis, currency arbitrage analysis, and interactive production calculators.

## 🏗️ Project Structure

```
eclesiar/
├── main.py                           # Main entry point with interactive menu
├── orchestrator.py                   # Main application orchestrator
├── reporting.py                      # Daily report generation
├── production_analyzer_consolidated.py  # Regional productivity analysis
├── arbitrage_analyzer_consolidated.py   # Currency arbitrage analysis
├── production_calculator.py          # Interactive production calculator
├── quick_calculator.py               # Quick production calculator (test scenarios)
├── short_economic_report.py          # Short economic report generator
├── api_client.py                     # API client
├── economy.py                        # Economic functions
├── military.py                       # Military functions
├── regions.py                        # Regional functions
├── storage.py                        # Data management
├── db.py                            # SQLite database
├── config.py                         # Configuration
├── arbitrage_config.py               # Arbitrage configuration
├── production_config.py              # Production analysis configuration
├── requirements.txt                  # Python dependencies
├── reports/                          # Daily reports (DOCX, HTML)
├── production_analysis/              # Productivity analysis
├── arbitrage_reports/                # Arbitrage reports
└── CALCULATOR_README.md              # Production calculator documentation
```

## 🚀 Getting Started

### Install dependencies
```bash
pip install -r requirements.txt
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
API_KEY=your_api_key_here
API_URL=https://api.eclesiar.com
ECLESIAR_DB_PATH=eclesiar.db
```

### Arbitrage configuration (arbitrage_config.py)
```python
ARBITRAGE_CONFIG = {
    'min_profit_threshold': 0.5,  # Minimum profit in %
    'max_risk_score': 0.7,        # Maximum risk score
    'ticket_cost_gold': 0.1,      # Ticket cost in gold
    'max_execution_time': 300     # Maximum execution time in seconds
}
```

## 📁 Report Organization

### Daily reports
- **Location**: `reports/`
- **Formats**: DOCX, HTML
- **Naming**: `raport_dzienny_YYYY-MM-DD_HH-MM.docx`

### Productivity analysis
- **Location**: `production_analysis/`
- **Formats**: TXT
- **Naming**: `production_analysis_YYYYMMDD_HHMMSS.txt`

### Arbitrage reports
- **Location**: `arbitrage_reports/`
- **Formats**: CSV, TXT
- **Naming**: `arbitrage_report_YYYYMMDD_HHMMSS.csv`

### Short economic reports
- **Location**: `reports/`
- **Formats**: DOCX
- **Naming**: `skrocony_raport_ekonomiczny_YYYY-MM-DD_HH-MM.docx`

## 🔧 Development

### Adding new modules
1. Create new Python file in main directory
2. Add import in `main.py`
3. Add new command in argument parser
4. Update documentation

### Testing
```bash
# Test single module
python -c "from production_analyzer_consolidated import ProductionAnalyzer; print('OK')"

# Test full application
python main.py full-analysis
```

## 📝 Changelog

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
