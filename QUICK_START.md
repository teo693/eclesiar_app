# Quick Start Guide

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone <repository-url>
cd eclesiar_app
```

### 2. Install Dependencies
```bash
pip install -r requirements/base.txt
```

### 3. Configure Environment
```bash
# Copy example configuration
cp env.example .env

# Edit with your API key
nano .env
```

Add your Eclesiar API key:
```bash
AUTH_TOKEN="eclesiar_prod_YOUR_API_KEY_HERE"
```

### 4. Run the Application
```bash
python3 main.py
```

## 📊 Available Reports

### Daily Report
```bash
python3 main.py daily-report
```

### Short Economic Report
```bash
python3 main.py short-economic-report
```

### Google Sheets Report
```bash
python3 main.py google-sheets-report
```

### Production Analysis
```bash
python3 main.py production-analysis
```

### Arbitrage Analysis
```bash
python3 main.py arbitrage-analysis
```

## 🔧 Google Sheets Integration

For Google Sheets integration, see [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md)

## 🔐 Security

**Never commit sensitive files!** See [SECURITY.md](SECURITY.md) for details.

## 📁 Important Files

- `env.example` - Configuration template (safe to commit)
- `.env` - Your configuration (NEVER commit)
- `cred/` - Credentials directory (NEVER commit)
- `data/` - Database and cache files (NEVER commit)
- `reports/` - Generated reports (NEVER commit)

## 🆘 Troubleshooting

### API Connection Issues
1. Check your API key in `.env`
2. Verify the key format: `eclesiar_prod_...`
3. Test API access manually

### Google Sheets Issues
1. Check [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md)
2. Verify service account permissions
3. Ensure APIs are enabled in Google Cloud Console

### Permission Errors
1. Check file permissions
2. Ensure directories exist (`data/`, `cred/`, `reports/`)
3. Run with appropriate user permissions

## 📚 Documentation

- [SECURITY.md](SECURITY.md) - Security guidelines
- [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) - Google Sheets setup
- [docs/](docs/) - Detailed documentation
