"""
Google Sheets Configuration

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import os
from pathlib import Path

# Google Sheets Configuration
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "cred/google_credentials.json")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "")
GOOGLE_SERVICE_ACCOUNT_EMAIL = os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL", "")

# Existing Spreadsheet ID (if you want to use existing spreadsheet instead of creating new one)
GOOGLE_SHEETS_EXISTING_ID = os.getenv("GOOGLE_SHEETS_EXISTING_ID", "")

# Report Settings
GOOGLE_SHEETS_REPORT_PREFIX = "Eclesiar Report"
GOOGLE_SHEETS_DATE_FORMAT = "%Y-%m-%d %H:%M"

# Sharing Settings
GOOGLE_SHEETS_SHARE_EMAILS = []  # Add user emails here
GOOGLE_SHEETS_DEFAULT_PERMISSION = "reader"  # "reader" or "writer"

# API Settings
GOOGLE_SHEETS_API_VERSION = "v4"
GOOGLE_SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def validate_google_sheets_config():
    """Validate Google Sheets configuration"""
    errors = []
    
    if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
        errors.append(f"Credentials file not found: {GOOGLE_CREDENTIALS_PATH}")
    
    if not GOOGLE_PROJECT_ID:
        errors.append("Google Project ID not set")
    
    if not GOOGLE_SERVICE_ACCOUNT_EMAIL:
        errors.append("Service Account Email not set")
    
    return errors

if __name__ == "__main__":
    errors = validate_google_sheets_config()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Google Sheets configuration is valid")
