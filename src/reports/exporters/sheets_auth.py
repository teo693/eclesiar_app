"""
Google Sheets Authentication Module

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import os
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import Optional

class GoogleSheetsAuth:
    """Handles Google Sheets API authentication"""
    
    def __init__(self, credentials_path: str = "cred/google_credentials.json"):
        self.credentials_path = credentials_path
        self.service = None
        self._validate_credentials()
    
    def _validate_credentials(self) -> None:
        """Validate credentials file exists"""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
    
    def authenticate(self) -> object:
        """Authenticate with Google Sheets API"""
        if self.service is not None:
            return self.service
        
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Try Application Default Credentials first
            try:
                from google.auth import default
                creds, project = default(scopes=scopes)
                print("✅ Using Application Default Credentials")
            except Exception as adc_error:
                print(f"⚠️ ADC failed: {adc_error}, trying service account file")
                # Fallback to service account file
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
                creds = Credentials.from_service_account_file(
                    self.credentials_path, 
                    scopes=scopes
                )
                print("✅ Using service account file")
            
            self.service = build('sheets', 'v4', credentials=creds)
            return self.service
            
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google Sheets API: {e}")
    
    def get_drive_service(self) -> object:
        """Get Google Drive service for file management"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Try Application Default Credentials first
            try:
                from google.auth import default
                creds, project = default(scopes=scopes)
            except Exception as adc_error:
                # Fallback to service account file
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
                creds = Credentials.from_service_account_file(
                    self.credentials_path, 
                    scopes=scopes
                )
            
            return build('drive', 'v3', credentials=creds)
            
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google Drive API: {e}")
