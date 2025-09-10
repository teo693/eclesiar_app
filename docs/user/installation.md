# Eclesiar App Installation Guide

## 🔐 API Configuration

### **1. Copy configuration file:**
```bash
cp .env.example .env
```

### **2. Edit .env file:**
```bash
nano .env
```

### **3. Set your API key:**
```bash
# Replace YOUR_API_KEY_HERE with your real API key
AUTH_TOKEN="eclesiar_prod_YOUR_REAL_API_KEY"
```

### **4. Test configuration:**
```bash
# Test API connection
curl -H "Authorization: Bearer eclesiar_prod_YOUR_KEY" https://api.eclesiar.com/countries
```

## 🚀 Running the Application

### **Interactive Mode:**
```bash
python3 main.py
```

### **Command Mode:**
```bash
# Short economic report
python3 main.py short-economic-report

# Regional productivity analysis
python3 main.py production-analysis

# Currency arbitrage analysis
python3 main.py arbitrage-analysis

# Interactive production calculator
python3 main.py production-calculator

# Quick production calculator
python3 main.py quick-calculator

# Full analysis
python3 main.py full-analysis
```

## 📁 File Structure

### **Configuration files:**
- `.env.example` - example configuration (safe to commit)
- `.env` - actual configuration (ignored by Git)

### **Files ignored by Git:**
- `.env` - contains sensitive data (API keys)
- `*.db` - databases
- `__pycache__/` - Python cache
- `reports/` - generated reports
- `*.log` - log files

## ⚠️ Security

### **Never commit:**
- `.env` file with real API keys
- Files with sensitive data
- Authorization keys

### **Always commit:**
- `.env.example` file (without real keys)
- `.gitignore` file
- Source code

## 🔧 Troubleshooting

### **401 Unauthorized Error:**
1. Check if API key is complete
2. Check if key hasn't expired
3. Check format: `eclesiar_prod_YOUR_KEY`

### **No API access:**
- Use sample report for testing
- Contact Eclesiar administration

## 📊 Application Features

### **Short Economic Report:**
- Currency rates vs GOLD
- Cheapest items by type
- Production examples (Q1-Q5) for each product
- **Enhanced tables** with regional and country bonus columns

### **Regional Productivity Analysis:**
- All 8 production factors
- **Regional bonuses** - region-specific production bonuses
- **Country bonuses** - dynamic calculation based on regional bonuses
- Regional comparison
- Company location optimization

### **Production Calculator:**
- **Interactive Calculator**: Full-featured with region selection and parameter configuration
- **Quick Calculator**: Fast testing of different scenarios
- **Country Bonus Integration**: Automatic calculation and display of country bonuses
- Real-time data from API

### **Currency Arbitrage Analysis:**
- Arbitrage opportunity detection
- Risk analysis
- Profit optimization

## 🌍 Internationalization

The application is fully translated to English:
- **User Interface**: All menus, prompts, and messages in English
- **Error Messages**: All error messages and warnings in English
- **Reports**: All generated reports use English terminology
- **Console Output**: All console output and logging in English

## 📞 Support

If you have configuration problems:
1. Check `API_TROUBLESHOOTING.md`
2. Check application logs
3. Contact Eclesiar administration

---

**Version**: 2.0  
**Date**: 2025-09-10  
**Features**: Country bonus system, English translation, enhanced functionality