# Google Sheets Integration Plan for Eclesiar Application

## 📋 **Implementation Status**
- ✅ **Google Cloud Project**: `your-project-id`
- ✅ **Service Account**: `your-service-account@your-project.iam.gserviceaccount.com`
- ✅ **Credentials File**: `cred/google_credentials.json`
- ✅ **Google Sheets API**: Enabled
- ✅ **Google Drive API**: Enabled

## 🎯 **Objective**
Adding "Google Sheets Report" option to the application menu that will generate reports directly to Google Sheets.

## 📁 **File Structure to Create**

```
src/reports/exporters/
├── google_sheets_exporter.py      # Main exporter
├── sheets_formatter.py            # Data formatting
├── sheets_auth.py                 # Google API authorization
└── sheets_templates.py            # Sheet templates

config/
├── google_credentials.json        # ✅ READY
└── settings/
    └── google_sheets.py           # Google Sheets configuration
```

## 🔧 **Step 1: Dependencies Update**

### 1.1. Add to `requirements/base.txt`
```txt
# Google Sheets API
google-api-python-client>=2.0.0
google-auth>=2.0.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
```

### 1.2. Install dependencies
```bash
pip install -r requirements/base.txt
```

## 🔧 **Step 2: Model Extension**

### 2.1. Update `src/core/models/entities.py`
```python
class ReportType(Enum):
    """Report types"""
    DAILY = "daily"
    PRODUCTION = "production"
    ARBITRAGE = "arbitrage"
    SHORT_ECONOMIC = "short_economic"
    HTML = "html"
    GOOGLE_SHEETS = "google_sheets"  # NEW TYPE
```

## 🔧 **Krok 3: Tworzenie Google Sheets Exporter**

### 3.1. `src/reports/exporters/sheets_auth.py`
```python
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
            
            creds = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scopes
            )
            
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
            
            creds = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scopes
            )
            
            return build('drive', 'v3', credentials=creds)
            
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google Drive API: {e}")
```

### 3.2. `src/reports/exporters/sheets_formatter.py`
```python
"""
Google Sheets Data Formatter

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json

class SheetsFormatter:
    """Formats data for Google Sheets export"""
    
    def __init__(self):
        self.date_format = "%Y-%m-%d %H:%M:%S"
    
    def format_daily_report(self, data: Dict[str, Any]) -> Dict[str, List[List]]:
        """Format daily report data for Google Sheets"""
        sheets_data = {}
        
        # Sheet 1: Podsumowanie
        summary_data = data.get('summary_data', {})
        sheets_data["Podsumowanie"] = [
            ["Eclesiar's Pulse - Raport Codzienny", ""],
            ["Data wygenerowania", datetime.now().strftime(self.date_format)],
            ["", ""],
            ["📊 STATYSTYKI OGÓLNE", ""],
            ["Liczba krajów", len(data.get('country_map', {}))],
            ["Liczba walut", len(data.get('currencies_map', {}))],
            ["Liczba wojowników", len(data.get('top_warriors', []))],
            ["", ""],
            ["📈 DANE ŹRÓDŁOWE", ""],
            ["Data pobrania", summary_data.get('fetched_at', 'N/A')],
            ["Status API", "Aktywne" if summary_data.get('fetched_at') else 'Błąd'],
        ]
        
        # Sheet 2: Kraje i Waluty
        countries_data = [["Kraj", "Waluta", "Kurs vs GOLD", "Status", "Region"]]
        country_map = data.get('country_map', {})
        currencies_map = data.get('currencies_map', {})
        
        for country_id, country_data in country_map.items():
            currency_id = country_data.get('currency_id')
            currency_info = currencies_map.get(currency_id, {})
            
            countries_data.append([
                country_data.get('name', 'N/A'),
                currency_info.get('name', 'N/A'),
                currency_info.get('gold_rate', 0),
                country_data.get('status', 'N/A'),
                country_data.get('region', 'N/A')
            ])
        
        sheets_data["Kraje i Waluty"] = countries_data
        
        # Sheet 3: Top Wojownicy
        warriors_data = [["Pozycja", "Nazwa", "Kraj", "Poziom", "Punkty"]]
        top_warriors = data.get('top_warriors', [])
        
        for i, warrior in enumerate(top_warriors[:20], 1):  # Top 20
            country_name = "N/A"
            if 'nationality_id' in warrior:
                country_info = country_map.get(warrior['nationality_id'], {})
                country_name = country_info.get('name', 'N/A')
            
            warriors_data.append([
                i,
                warrior.get('username', 'N/A'),
                country_name,
                warrior.get('level', 0),
                warrior.get('points', 0)
            ])
        
        sheets_data["Top Wojownicy"] = warriors_data
        
        # Sheet 4: Produkcja (jeśli dostępna)
        if 'production_data' in data:
            production_data = data['production_data']
            prod_sheet = [["Region", "Kraj", "Przedmiot", "Efektywność", "Zanieczyszczenie"]]
            
            for item in production_data[:50]:  # Top 50
                prod_sheet.append([
                    item.get('region_name', 'N/A'),
                    item.get('country_name', 'N/A'),
                    item.get('item_name', 'N/A'),
                    item.get('efficiency_score', 0),
                    item.get('pollution', 0)
                ])
            
            sheets_data["Produkcja"] = prod_sheet
        
        return sheets_data
    
    def format_economic_report(self, data: Dict[str, Any]) -> Dict[str, List[List]]:
        """Format economic report data for Google Sheets"""
        sheets_data = {}
        
        # Sheet 1: Kursy Walut
        currency_rates = data.get('currency_rates', {})
        rates_data = [["Waluta", "Kurs vs GOLD", "Zmiana (%)", "Status"]]
        
        for currency_id, rate_data in currency_rates.items():
            rates_data.append([
                rate_data.get('name', 'N/A'),
                rate_data.get('gold_rate', 0),
                rate_data.get('change_percent', 0),
                "Wzrost" if rate_data.get('change_percent', 0) > 0 else "Spadek"
            ])
        
        sheets_data["Kursy Walut"] = rates_data
        
        # Sheet 2: Najtańsze Przedmioty
        cheapest_items = data.get('cheapest_items', {})
        items_data = [["Przedmiot", "Kraj", "Cena", "Waluta", "Dostępność"]]
        
        for item_type, item_data in cheapest_items.items():
            items_data.append([
                item_data.get('name', 'N/A'),
                item_data.get('country', 'N/A'),
                item_data.get('price', 0),
                item_data.get('currency', 'N/A'),
                item_data.get('availability', 'N/A')
            ])
        
        sheets_data["Najtańsze Przedmioty"] = items_data
        
        return sheets_data
    
    def format_production_report(self, data: Dict[str, Any]) -> Dict[str, List[List]]:
        """Format production report data for Google Sheets"""
        sheets_data = {}
        
        production_data = data.get('production_data', [])
        
        # Sheet 1: Ranking Regionów
        ranking_data = [["Pozycja", "Region", "Kraj", "Efektywność", "Zanieczyszczenie", "Bonus"]]
        
        for i, item in enumerate(production_data[:30], 1):  # Top 30
            ranking_data.append([
                i,
                item.get('region_name', 'N/A'),
                item.get('country_name', 'N/A'),
                item.get('efficiency_score', 0),
                item.get('pollution', 0),
                item.get('total_bonus', 0)
            ])
        
        sheets_data["Ranking Regionów"] = ranking_data
        
        return sheets_data
```

### 3.3. `src/reports/exporters/google_sheets_exporter.py`
```python
"""
Google Sheets Report Exporter

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .sheets_auth import GoogleSheetsAuth
from .sheets_formatter import SheetsFormatter
from ..factories.report_factory import ReportGenerator
from ...core.models.entities import ReportType
from ...core.services.base_service import ServiceDependencies

class GoogleSheetsExporter(ReportGenerator):
    """Google Sheets report generator"""
    
    def __init__(self, dependencies: ServiceDependencies):
        super().__init__(dependencies)
        self.auth = GoogleSheetsAuth()
        self.formatter = SheetsFormatter()
    
    def generate(self, data: Dict[str, Any], sections: Dict[str, bool], 
                output_dir: str) -> Optional[str]:
        """Generate Google Sheets report"""
        try:
            print("🔄 Generating Google Sheets report...")
            
            # Authenticate with Google Sheets
            service = self.auth.authenticate()
            drive_service = self.auth.get_drive_service()
            
            # Determine report type and format data
            report_type = self._determine_report_type(data)
            formatted_data = self._format_data_by_type(data, report_type)
            
            # Create spreadsheet
            spreadsheet_id = self._create_spreadsheet(formatted_data, report_type, service)
            
            # Share spreadsheet (optional)
            self._share_spreadsheet(spreadsheet_id, drive_service)
            
            # Get spreadsheet URL
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
            print(f"✅ Google Sheets report created: {spreadsheet_url}")
            return spreadsheet_url
            
        except Exception as e:
            print(f"❌ Error generating Google Sheets report: {e}")
            return None
    
    def _determine_report_type(self, data: Dict[str, Any]) -> str:
        """Determine report type based on data content"""
        if 'production_data' in data:
            return 'production'
        elif 'currency_rates' in data:
            return 'economic'
        else:
            return 'daily'
    
    def _format_data_by_type(self, data: Dict[str, Any], report_type: str) -> Dict[str, List[List]]:
        """Format data based on report type"""
        if report_type == 'production':
            return self.formatter.format_production_report(data)
        elif report_type == 'economic':
            return self.formatter.format_economic_report(data)
        else:
            return self.formatter.format_daily_report(data)
    
    def _create_spreadsheet(self, formatted_data: Dict[str, List[List]], 
                           report_type: str, service) -> str:
        """Create Google Sheets spreadsheet"""
        
        # Create spreadsheet
        spreadsheet_body = {
            'properties': {
                'title': f"Eclesiar Report - {report_type.title()} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            },
            'sheets': []
        }
        
        # Add sheets
        for sheet_name, sheet_data in formatted_data.items():
            sheet = {
                'properties': {
                    'title': sheet_name,
                    'gridProperties': {
                        'rowCount': len(sheet_data),
                        'columnCount': max(len(row) for row in sheet_data) if sheet_data else 1
                    }
                },
                'data': [{
                    'values': [{'userEnteredValue': {'stringValue': str(cell)} for cell in row} 
                              for row in sheet_data]
                }]
            }
            spreadsheet_body['sheets'].append(sheet)
        
        # Create the spreadsheet
        spreadsheet = service.spreadsheets().create(body=spreadsheet_body).execute()
        spreadsheet_id = spreadsheet['spreadsheetId']
        
        # Format the spreadsheet
        self._format_spreadsheet(spreadsheet_id, service)
        
        return spreadsheet_id
    
    def _format_spreadsheet(self, spreadsheet_id: str, service) -> None:
        """Apply formatting to the spreadsheet"""
        try:
            # Get sheet properties
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            
            # Format headers (first row of each sheet)
            requests = []
            for sheet in spreadsheet['sheets']:
                sheet_id = sheet['properties']['sheetId']
                sheet_name = sheet['properties']['title']
                
                # Format header row
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
                                'textFormat': {
                                    'foregroundColor': {'red': 1, 'green': 1, 'blue': 1},
                                    'bold': True
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                })
            
            # Apply formatting
            if requests:
                body = {'requests': requests}
                service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id, 
                    body=body
                ).execute()
                
        except Exception as e:
            print(f"⚠️ Warning: Could not apply formatting: {e}")
    
    def _share_spreadsheet(self, spreadsheet_id: str, drive_service) -> None:
        """Share spreadsheet with users (optional)"""
        try:
            # Get spreadsheet info
            spreadsheet = drive_service.files().get(fileId=spreadsheet_id).execute()
            
            # Make it viewable by anyone with the link
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            drive_service.permissions().create(
                fileId=spreadsheet_id,
                body=permission
            ).execute()
            
            print(f"📤 Spreadsheet shared: {spreadsheet['webViewLink']}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not share spreadsheet: {e}")
    
    def get_report_type(self) -> ReportType:
        return ReportType.GOOGLE_SHEETS
```

## 🔧 **Krok 4: Aktualizacja Factory Pattern**

### 4.1. Aktualizuj `src/reports/factories/report_factory.py`
```python
# Dodaj import
from ..exporters.google_sheets_exporter import GoogleSheetsExporter

# Aktualizuj _generators
_generators = {
    ReportType.DAILY: DailyReportGenerator,
    ReportType.HTML: HTMLReportGenerator,
    ReportType.PRODUCTION: ProductionReportGenerator,
    ReportType.ARBITRAGE: ArbitrageReportGenerator,
    ReportType.SHORT_ECONOMIC: ShortEconomicReportGenerator,
    ReportType.GOOGLE_SHEETS: GoogleSheetsExporter,  # NOWY
}
```

## 🔧 **Krok 5: Aktualizacja Menu Aplikacji**

### 5.1. Aktualizuj `main.py`
```python
def interactive_menu():
    """Interactive menu for report generation"""
    while True:
        print("\n" + "="*50)
        print("🎯 ECLESIAR REPORT GENERATOR")
        print("="*50)
        print("1. Generate Daily Report (DOCX)")
        print("2. Generate HTML Report")
        print("3. Generate Production Analysis")
        print("4. Generate Arbitrage Report")
        print("5. Generate Short Economic Report")
        print("6. Generate Google Sheets Report")  # NOWA OPCJA
        print("7. Generate All Report Types")
        print("8. Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == "1":
            generate_daily_report()
        elif choice == "2":
            generate_html_report()
        elif choice == "3":
            generate_production_analysis()
        elif choice == "4":
            generate_arbitrage_report()
        elif choice == "5":
            generate_short_economic_report()
        elif choice == "6":  # NOWA OPCJA
            generate_google_sheets_report()
        elif choice == "7":
            generate_all_reports()
        elif choice == "8":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def generate_google_sheets_report():
    """Generate Google Sheets report"""
    print("\n🔄 Generating Google Sheets Report...")
    
    try:
        # Use existing orchestrator service
        from src.core.services.orchestrator_service_refactored import OrchestratorService
        from src.core.container import Container
        
        container = Container()
        orchestrator = OrchestratorService(container)
        
        # Default sections
        sections = {
            'military': True,
            'warriors': True, 
            'economic': True,
            'production': True
        }
        
        # Generate report
        result = orchestrator._generate_report(
            data={},  # Will be fetched by orchestrator
            sections=sections,
            report_type="google_sheets",
            output_dir="reports"
        )
        
        if result:
            print(f"✅ Google Sheets report generated successfully!")
            print(f"📊 Report URL: {result}")
        else:
            print("❌ Failed to generate Google Sheets report")
            
    except Exception as e:
        print(f"❌ Error generating Google Sheets report: {e}")
```

## 🔧 **Krok 6: Aktualizacja Orchestrator Service**

### 6.1. Aktualizuj `src/core/services/orchestrator_service_refactored.py`
```python
# W metodzie _generate_report, dodaj do report_type_mapping:
report_type_mapping = {
    "daily": ReportType.DAILY,
    "html": ReportType.HTML,
    "production": ReportType.PRODUCTION,
    "arbitrage": ReportType.ARBITRAGE,
    "short_economic": ReportType.SHORT_ECONOMIC,
    "google_sheets": ReportType.GOOGLE_SHEETS  # NOWY
}
```

## 🔧 **Krok 7: Konfiguracja**

### 7.1. Utwórz `config/settings/google_sheets.py`
```python
"""
Google Sheets Configuration

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import os
from pathlib import Path

# Google Sheets Configuration
GOOGLE_CREDENTIALS_PATH = "cred/google_credentials.json"
GOOGLE_PROJECT_ID = "your-project-id"
GOOGLE_SERVICE_ACCOUNT_EMAIL = "your-service-account@your-project.iam.gserviceaccount.com"

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
```

## 🔧 **Krok 8: Aktualizacja .gitignore**

### 8.1. Dodaj do `.gitignore`
```gitignore
# Google Sheets credentials
cred/google_credentials.json
config/google_sheets_config.py
```

## 🧪 **Krok 9: Testowanie**

### 9.1. Test Konfiguracji
```bash
# Test konfiguracji
python3 config/settings/google_sheets.py

# Test autoryzacji
python3 -c "
from src.reports.exporters.sheets_auth import GoogleSheetsAuth
auth = GoogleSheetsAuth()
service = auth.authenticate()
print('✅ Google Sheets API connection successful!')
"
```

### 9.2. Test Generowania Raportu
```bash
# Uruchom aplikację i wybierz opcję 6
python3 main.py
```

## 📋 **Harmonogram Implementacji**

### **Faza 1: Podstawowa Integracja (1-2 dni)**
- [ ] Aktualizacja requirements
- [ ] Tworzenie podstawowych modułów (auth, formatter, exporter)
- [ ] Test połączenia z Google Sheets API

### **Faza 2: Integracja z Aplikacją (1-2 dni)**
- [ ] Aktualizacja Factory Pattern
- [ ] Dodanie opcji do menu
- [ ] Integracja z Orchestrator Service

### **Faza 3: Formatowanie i Optymalizacja (1 dzień)**
- [ ] Poprawa formatowania arkuszy
- [ ] Dodanie kolorowania i stylów
- [ ] Testy z różnymi typami raportów

### **Faza 4: Produkcja (1 dzień)**
- [ ] Finalne testy
- [ ] Dokumentacja
- [ ] Deploy

## ✅ **Oczekiwane Rezultaty**

Po implementacji użytkownik będzie mógł:

1. **Wybrać opcję 6** w menu aplikacji
2. **Wygenerować raport** bezpośrednio do Google Sheets
3. **Otrzymać link** do utworzonego arkusza
4. **Zobaczyć sformatowane dane** w różnych arkuszach
5. **Udostępnić arkusz** innym użytkownikom

## 🎯 **Korzyści**

- ✅ **Dostęp online** - raporty dostępne w przeglądarce
- ✅ **Współdzielenie** - łatwe udostępnianie zespołowi
- ✅ **Wizualizacje** - wbudowane narzędzia Google Sheets
- ✅ **Aktualizacja** - możliwość edycji i komentowania
- ✅ **Integracja** - łączenie z innymi narzędziami Google

---

**Status**: ✅ Plan gotowy do implementacji
**Czas realizacji**: 4-6 dni
**Priorytet**: Wysoki
