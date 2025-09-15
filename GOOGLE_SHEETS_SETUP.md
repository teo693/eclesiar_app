# Google Sheets Integration Setup Guide

## 🔐 Security Notice

**IMPORTANT**: This application contains sensitive configuration data that should NOT be committed to GitHub. The following files are automatically ignored by Git:

- `.env` - Contains API keys and sensitive configuration
- `cred/google_credentials.json` - Google service account credentials
- `data/*.db` - Database files
- `reports/` - Generated reports

## 📋 Prerequisites

1. **Google Cloud Project** with Google Sheets API and Google Drive API enabled
2. **Service Account** with appropriate permissions
3. **Google Sheets spreadsheet** (existing or new)

## 🚀 Setup Instructions

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Google Sheets API
   - Google Drive API

### Step 2: Create Service Account

1. In Google Cloud Console, go to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Fill in details:
   - **Name**: `eclesiar-sheets-service`
   - **Description**: `Service account for Eclesiar Google Sheets integration`
4. Click **Create and Continue**
5. Grant roles:
   - **Google Sheets API > Editor**
   - **Google Drive API > Editor**
6. Click **Done**

### Step 3: Generate Credentials

1. Find your service account in the list
2. Click on the service account email
3. Go to **Keys** tab
4. Click **Add Key > Create new key**
5. Select **JSON** format
6. Download the JSON file
7. Save it as `cred/google_credentials.json`

### Step 4: Configure Environment Variables

1. Copy the example configuration:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` file and fill in your values:
   ```bash
   # Google Sheets Configuration
   GOOGLE_PROJECT_ID="your-google-project-id"
   GOOGLE_SERVICE_ACCOUNT_EMAIL="your-service-account@your-project.iam.gserviceaccount.com"
   GOOGLE_SHEETS_EXISTING_ID="your-spreadsheet-id-here"
   ```

### Step 5: Create or Configure Spreadsheet

#### Option A: Use Existing Spreadsheet
1. Open your Google Sheets spreadsheet
2. Copy the spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```
3. Add the ID to your `.env` file:
   ```bash
   GOOGLE_SHEETS_EXISTING_ID="your-spreadsheet-id-here"
   ```

#### Option B: Let Application Create New Spreadsheet
1. Leave `GOOGLE_SHEETS_EXISTING_ID` empty in `.env`
2. The application will create a new spreadsheet each time

### Step 6: Share Spreadsheet (if using existing)

1. Open your Google Sheets spreadsheet
2. Click **Share** button
3. Add your service account email with **Editor** permissions
4. The service account email format: `your-service-account@your-project.iam.gserviceaccount.com`

## 🏃‍♂️ Running Google Sheets Reports

### Command Line Usage

```bash
# Generate Google Sheets report
python3 main.py google-sheets-report

# Generate with specific sections
python3 main.py google-sheets-report --sections economic,production
```

### Interactive Mode

```bash
python3 main.py
# Select "Google Sheets Report" from the menu
```

## 📊 Report Structure

The Google Sheets report contains the following sheets:

1. **Summary** - General statistics and overview
2. **Cheapest Items** - Lowest prices with currency, amount, and 5-day average
3. **Currency Rates** - Exchange rates with growth indicators
4. **Production Regions** - Regional productivity analysis

## 🔧 Troubleshooting

### Common Issues

#### 1. Permission Denied (403 Error)
```
❌ Error generating Google Sheets report: Permission denied
```

**Solution:**
1. Check if service account has correct roles
2. Ensure Google Sheets API and Google Drive API are enabled
3. Verify spreadsheet sharing permissions
4. Wait a few minutes for permissions to propagate

#### 2. Credentials File Not Found
```
❌ Credentials file not found: cred/google_credentials.json
```

**Solution:**
1. Ensure `cred/google_credentials.json` exists
2. Check file permissions
3. Verify the path in your `.env` file

#### 3. Invalid Spreadsheet ID
```
❌ Invalid spreadsheet ID
```

**Solution:**
1. Verify the spreadsheet ID in your `.env` file
2. Ensure the spreadsheet exists and is accessible
3. Check if the service account has access to the spreadsheet

### Validation Commands

```bash
# Validate Google Sheets configuration
python3 -c "from config.settings.google_sheets import validate_google_sheets_config; print('✅ Valid' if not validate_google_sheets_config() else '❌ Invalid')"

# Test Google Sheets connection
python3 -c "from src.reports.exporters.sheets_auth import GoogleSheetsAuth; auth = GoogleSheetsAuth(); print('✅ Connected' if auth.authenticate() else '❌ Failed')"
```

## 🔒 Security Best Practices

1. **Never commit sensitive files:**
   - `.env` files
   - `cred/google_credentials.json`
   - Database files
   - Generated reports

2. **Use environment variables** for all sensitive configuration

3. **Regularly rotate** service account keys

4. **Limit permissions** to only what's necessary

5. **Monitor API usage** in Google Cloud Console

## 📝 File Structure

```
eclesiar_app/
├── cred/
│   └── google_credentials.json          # Service account credentials (IGNORED)
├── config/
│   └── settings/
│       └── google_sheets.py             # Configuration (safe to commit)
├── src/
│   └── reports/
│       └── exporters/
│           ├── google_sheets_exporter.py # Main exporter
│           ├── sheets_auth.py           # Authentication
│           └── sheets_formatter.py      # Data formatting
├── .env                                 # Your configuration (IGNORED)
├── env.example                          # Example configuration (safe to commit)
└── GOOGLE_SHEETS_SETUP.md              # This file
```

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your Google Cloud project configuration
3. Ensure all required APIs are enabled
4. Check service account permissions
5. Review the application logs for detailed error messages

## 📚 Additional Resources

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [Service Account Authentication](https://developers.google.com/identity/protocols/oauth2/service-account)
